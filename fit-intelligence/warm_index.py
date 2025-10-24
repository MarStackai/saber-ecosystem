#!/usr/bin/env python3
"""
In-memory warm index for reliable geographic filtering
Bypasses ChromaDB's unreliable WHERE clause filtering
"""

import numpy as np
import logging
import re

logger = logging.getLogger(__name__)

TECH_ALIASES = {
    'solar': 'photovoltaic',
    'solar pv': 'photovoltaic',
    'pv': 'photovoltaic',
    'pv panels': 'photovoltaic',
    'solar panels': 'photovoltaic',
    'wind turbines': 'wind',
    'wind farms': 'wind',
    'turbines': 'wind',
    'water power': 'hydro',
    'hydroelectric': 'hydro',
    'hydro power': 'hydro',
    'biogas': 'anaerobic digestion',
    'ad': 'anaerobic digestion',
    'biogas plants': 'anaerobic digestion'
}

ALLOWED_TECH = {'photovoltaic', 'wind', 'hydro', 'anaerobic digestion'}

def canonical_tech(value):
    """Normalize technology names to canonical form"""
    if not value:
        return None
    tech = TECH_ALIASES.get(str(value).strip().lower(), str(value).strip().lower())
    return tech if tech in ALLOWED_TECH else None

class WarmIndex:
    """Pre-load all embeddings and metadata for reliable filtering"""
    
    def __init__(self, collection, embedder):
        self.c = collection
        self.embedder = embedder
        self.ids = []
        self.emb = []
        self.meta = []
        
        # Load all data into memory
        logger.info("Loading warm index into memory...")
        off = 0
        bs = 5000
        while True:
            # Fixed: Remove "ids" from include list to avoid ChromaDB error
            r = self.c.get(include=["embeddings", "metadatas"], limit=bs, offset=off)
            if not r or not r.get("ids"):
                break
            self.ids.extend(r["ids"])
            self.emb.extend(r["embeddings"])
            self.meta.extend(r["metadatas"])
            off += len(r["ids"])
            logger.info(f"Loaded {len(self.ids)} records...")
        
        logger.info(f"Warm index ready with {len(self.ids)} records")
        
        # Build area map for exact area matching (e.g., M not ML)
        self.area_map = {}
        self.prefix_map = {}
        
        for i, m in enumerate(self.meta):
            # Map by postcode area - try postcode_area field first, then extract from postcode
            a = str(m.get("postcode_area") or "").upper()
            if not a:
                # Extract area from postcode if postcode_area field missing
                pc = str(m.get("postcode", "")).upper().strip()
                match = re.match(r'([A-Z]{1,2})', pc)
                if match:
                    a = match.group(1)
            
            if a:
                self.area_map.setdefault(a, []).append(i)
            
            # Also maintain prefix map for backwards compatibility
            p = str(m.get("postcode_prefix") or m.get("postcode", "")[:2]).upper()
            if p:
                self.prefix_map.setdefault(p, []).append(i)
    
    def _qemb(self, text):
        """Generate normalized query embedding"""
        v = self.embedder.encode([text])[0]
        v = np.asarray(v, dtype="float32")
        n = np.linalg.norm(v)
        return v if n == 0 else v / n
    
    def search(self, query_text, areas=None, prefixes=None, technology=None, min_kw=None, max_kw=None, repowering_window=None, min_years_left=None, max_years_left=None, top_k=200):
        """Search with guaranteed geographic filtering using exact area matching"""
        q = self._qemb(query_text)
        
        # Assert area/outward equality - prevent M matching ML
        if areas:
            areas = [a.upper().strip() for a in areas if a]
            # Validate area codes are exact (M is M, not ML)
            for area in areas:
                if area == 'M' and 'ML' in areas:
                    logger.warning(f"Area assertion failed: M and ML both present, removing ML")
                    areas = [a for a in areas if a != 'ML']
                elif area == 'AB' and any(a.startswith('AB') and a != 'AB' for a in areas):
                    logger.warning(f"Area assertion: AB should be exact, not AB prefixes")
                    areas = [a for a in areas if a == 'AB' or not a.startswith('AB')]
        
        # Get candidate indices based on areas or prefixes
        cand_idx = []
        
        if areas:
            # Use exact area matching (M won't match ML)
            for a in {x.upper() for x in areas}:
                cand_idx.extend(self.area_map.get(a, []))
            if not cand_idx:
                logger.warning(f"No records found for areas: {areas}")
                return []
        elif prefixes:
            # Fallback to prefix matching if areas not provided
            for p in {x.upper() for x in prefixes}:
                cand_idx.extend(self.prefix_map.get(p, []))
            if not cand_idx:
                logger.warning(f"No records found for prefixes: {prefixes}")
                return []
        else:
            cand_idx = list(range(len(self.ids)))
        
        # Compute similarities
        em = np.asarray([self.emb[i] for i in cand_idx], dtype="float32")
        den = np.linalg.norm(em, axis=1, keepdims=True)
        den[den == 0] = 1
        em = em / den
        scores = em @ q
        order = np.argsort(-scores)
        
        # Filter and collect results
        out = []
        for j in order:
            i = cand_idx[j]
            m = self.meta[i]
            
            # Apply filters with technology aliasing
            if technology:
                normalized_tech = canonical_tech(technology)
                site_tech = canonical_tech(m.get("technology", ""))
                if normalized_tech and site_tech != normalized_tech:
                    continue
            
            kw = m.get("capacity_kw")
            if kw is not None:
                try:
                    kw = float(kw)
                    if min_kw is not None and kw < float(min_kw):
                        continue
                    if max_kw is not None and kw > float(max_kw):
                        continue
                except (ValueError, TypeError):
                    continue
            
            # Apply repowering window filter
            if repowering_window:
                window = m.get("repowering_window")
                if not window:
                    # Calculate it on the fly if not present
                    from financial_calculator import years_left, determine_repowering_window
                    years = years_left(m.get("fit_expiry_date"))
                    window = determine_repowering_window(years)
                
                if isinstance(repowering_window, str):
                    if window != repowering_window.upper():
                        continue
                elif isinstance(repowering_window, list):
                    if window not in [w.upper() for w in repowering_window]:
                        continue
            
            # Apply years_left range filter
            if min_years_left is not None or max_years_left is not None:
                from financial_calculator import years_left
                years = years_left(
                    m.get("fit_expiry_date"),
                    m.get("commission_date")
                )
                if years is not None:
                    if min_years_left is not None and years < float(min_years_left):
                        continue
                    if max_years_left is not None and years > float(max_years_left):
                        continue
            
            out.append((float(scores[j]), self.ids[i], m))
            if len(out) >= top_k:
                break
        
        return out