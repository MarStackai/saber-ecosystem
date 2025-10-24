#!/usr/bin/env python3
"""
Session-based Conversation Manager for FIT Intelligence
Maintains proper conversation state across queries
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages conversation sessions with proper state tracking"""
    
    def __init__(self, timeout_minutes: int = 30):
        self.sessions = {}  # session_id -> session data
        self.timeout = timeout_minutes * 60  # Convert to seconds
        
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create a session"""
        self._cleanup_old_sessions()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'created': time.time(),
                'last_activity': time.time(),
                'last_query': '',
                'last_results': [],
                'last_filter': {},
                'query_history': [],
                'context_locked': False  # When True, always use previous results
            }
            logger.info(f"Created new session: {session_id}")
        else:
            self.sessions[session_id]['last_activity'] = time.time()
            
        return self.sessions[session_id]
    
    def should_use_context(self, session_id: str, query: str) -> bool:
        """Determine if this query should use previous context"""
        session = self.get_session(session_id)
        query_lower = query.lower()
        
        # Strong indicators this is a follow-up
        strong_followup_phrases = [
            'give me all the details',
            'give me details',
            'show me details',
            'all the details',
            'more details',
            'their details',
            'those details',
            'calculate income',
            'their income',
            'fit income',
            'what about their',
            'tell me more',
            'show me more',
            'expand on',
            'elaborate',
            'break down'
        ]
        
        # Check for strong follow-up indicators
        for phrase in strong_followup_phrases:
            if phrase in query_lower:
                logger.info(f"Session {session_id}: Detected strong follow-up phrase: '{phrase}'")
                return True
        
        # Pronouns that reference previous results
        reference_words = ['their', 'those', 'these', 'them', 'that', 'the same', 'it']
        has_reference = any(word in query_lower.split() for word in reference_words)
        
        # Check if query lacks specifics (no technology, no location)
        technologies = ['wind', 'solar', 'hydro', 'photovoltaic', 'anaerobic']
        locations = ['yorkshire', 'scotland', 'wales', 'aberdeen', 'edinburgh', 'london', 
                    'manchester', 'birmingham', 'glasgow', 'cardiff']
        
        has_technology = any(tech in query_lower for tech in technologies)
        has_location = any(loc in query_lower for loc in locations)
        has_capacity = 'kw' in query_lower or 'mw' in query_lower
        
        # If it has references but no specifics, it's likely a follow-up
        if has_reference and not (has_technology or has_location or has_capacity):
            logger.info(f"Session {session_id}: Has references without specifics - using context")
            return True
        
        # Check if the query is asking for analysis/calculations on previous results
        analysis_keywords = ['calculate', 'analyze', 'compute', 'estimate', 'total', 'sum', 
                           'average', 'breakdown', 'income', 'revenue', 'earnings']
        if any(keyword in query_lower for keyword in analysis_keywords) and session['last_results']:
            logger.info(f"Session {session_id}: Analysis request on previous results")
            return True
        
        # If we have previous results and the query is very short, likely a follow-up
        if session['last_results'] and len(query.split()) <= 5 and has_reference:
            logger.info(f"Session {session_id}: Short query with references - using context")
            return True
        
        return False
    
    def store_results(self, session_id: str, query: str, results: List[Dict], filter_used: Dict = None):
        """Store query results in session"""
        session = self.get_session(session_id)
        
        session['last_query'] = query
        session['last_results'] = results
        session['last_filter'] = filter_used or {}
        
        # Add to history
        session['query_history'].append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'result_count': len(results),
            'filter': filter_used
        })
        
        # Keep only last 10 queries in history
        if len(session['query_history']) > 10:
            session['query_history'] = session['query_history'][-10:]
        
        logger.info(f"Session {session_id}: Stored {len(results)} results for '{query}'")
    
    def get_last_results(self, session_id: str) -> List[Dict]:
        """Get the last results from session"""
        session = self.get_session(session_id)
        return session['last_results']
    
    def lock_context(self, session_id: str):
        """Lock the context to prevent new searches"""
        session = self.get_session(session_id)
        session['context_locked'] = True
        logger.info(f"Session {session_id}: Context locked")
    
    def unlock_context(self, session_id: str):
        """Unlock the context to allow new searches"""
        session = self.get_session(session_id)
        session['context_locked'] = False
        logger.info(f"Session {session_id}: Context unlocked")
    
    def _cleanup_old_sessions(self):
        """Remove sessions older than timeout"""
        current_time = time.time()
        expired = []
        
        for session_id, session in self.sessions.items():
            if current_time - session['last_activity'] > self.timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
            logger.info(f"Expired session: {session_id}")
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get session information for debugging"""
        session = self.get_session(session_id)
        return {
            'session_id': session_id,
            'created': datetime.fromtimestamp(session['created']).isoformat(),
            'last_activity': datetime.fromtimestamp(session['last_activity']).isoformat(),
            'last_query': session['last_query'],
            'result_count': len(session['last_results']),
            'query_count': len(session['query_history']),
            'context_locked': session['context_locked']
        }