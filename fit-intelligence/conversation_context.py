#!/usr/bin/env python3
"""
Conversation Context Manager
Maintains context across queries for better conversational flow
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ConversationContext:
    """Manages conversation context and memory"""
    
    def __init__(self, timeout_minutes: int = 30):
        """
        Initialize conversation context manager
        
        Args:
            timeout_minutes: How long to keep context active
        """
        self.sessions = {}  # session_id -> context
        self.timeout_minutes = timeout_minutes
    
    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """Get existing session or create new one"""
        now = datetime.now()
        
        # Clean up old sessions
        self._cleanup_old_sessions()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'created_at': now,
                'last_active': now,
                'context': {
                    'location': None,
                    'capacity': None,
                    'capacity_min': None,
                    'capacity_max': None,
                    'technology': None,
                    'last_query': None,
                    'last_results_count': None,
                    'history': []
                }
            }
        else:
            self.sessions[session_id]['last_active'] = now
        
        return self.sessions[session_id]
    
    def update_context(self, session_id: str, query: str, 
                      extracted_entities: Dict, results_count: int) -> Dict:
        """
        Update session context with new query information
        
        Args:
            session_id: Session identifier
            query: User's query
            extracted_entities: Entities extracted from current query
            results_count: Number of results found
        
        Returns:
            Merged context with carry-over from previous queries
        """
        session = self.get_or_create_session(session_id)
        context = session['context']
        
        # Add to history
        context['history'].append({
            'query': query,
            'entities': extracted_entities,
            'results': results_count,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 10 queries in history
        if len(context['history']) > 10:
            context['history'] = context['history'][-10:]
        
        # Update context with new information
        context['last_query'] = query
        context['last_results_count'] = results_count
        
        # Intelligently merge entities
        merged_entities = self._merge_entities(context, extracted_entities, query)
        
        # Update stored context
        for key in ['location', 'capacity', 'capacity_min', 'capacity_max', 'technology']:
            if key in merged_entities:
                context[key] = merged_entities[key]
        
        logger.info(f"Session {session_id}: Updated context with query '{query}'")
        logger.info(f"Merged entities: {merged_entities}")
        
        return merged_entities
    
    def _merge_entities(self, context: Dict, new_entities: Dict, query: str) -> Dict:
        """
        Intelligently merge new entities with context
        
        Handles cases like:
        - "what about 300kw?" -> uses previous location
        - "or wind farms?" -> uses previous capacity and location
        - "stevenage i meant" -> correction to previous location
        """
        merged = {}
        query_lower = query.lower()
        
        # Check if this is a follow-up or correction
        is_followup = self._is_followup_query(query_lower)
        is_correction = self._is_correction(query_lower)
        
        # Handle corrections (like "stevenage i meant")
        if is_correction and 'location' in new_entities:
            # Replace the old location with the correction
            merged['location'] = new_entities['location']
            logger.info(f"Detected correction: location -> {merged['location']}")
        
        # Handle follow-ups (like "what about 300kw?")
        elif is_followup:
            # Start with previous context
            for key in ['location', 'technology', 'capacity', 'capacity_min', 'capacity_max']:
                if context.get(key):
                    merged[key] = context[key]
            
            # Override with new information if provided
            for key, value in new_entities.items():
                if value is not None:
                    merged[key] = value
                    logger.info(f"Follow-up override: {key} -> {value}")
        
        # Handle partial queries that reference previous context
        elif self._is_partial_query(query_lower, new_entities):
            # Use previous context for missing parts
            if not new_entities.get('location') and context.get('location'):
                merged['location'] = context['location']
                logger.info(f"Carrying over location: {context['location']}")
            
            if not new_entities.get('technology') and context.get('technology'):
                # Only carry over technology if query seems to want it
                if any(word in query_lower for word in ['sites', 'installations', 'farms', 'or']):
                    merged['technology'] = context['technology']
                    logger.info(f"Carrying over technology: {context['technology']}")
            
            # Always use new capacity if provided
            for key in ['capacity', 'capacity_min', 'capacity_max', 'technology', 'location']:
                if key in new_entities and new_entities[key] is not None:
                    merged[key] = new_entities[key]
        
        # Standard query - use new entities
        else:
            merged = new_entities.copy()
        
        # Handle special cases
        merged = self._handle_special_cases(merged, query_lower, context)
        
        return merged
    
    def _is_followup_query(self, query_lower: str) -> bool:
        """Check if query is a follow-up to previous"""
        followup_patterns = [
            r'^what about',
            r'^how about',
            r'^or\s+',
            r'^and\s+',
            r'^also\s+',
            r'^any\s+',
            r'^are there',
            r'^show me',
            r'^what if',
            r'^try\s+'
        ]
        
        for pattern in followup_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _is_correction(self, query_lower: str) -> bool:
        """Check if query is correcting previous input"""
        correction_patterns = [
            r'i meant',
            r'i mean',
            r'sorry',
            r'correction',
            r'actually',
            r'no,?\s+',
            r'not\s+.*but',
            r'^[a-z]+\s+i meant$'  # "stevenage i meant"
        ]
        
        for pattern in correction_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _is_partial_query(self, query_lower: str, entities: Dict) -> bool:
        """Check if query is partial and needs context"""
        # If query has capacity but no location, it's partial
        if ('capacity' in entities or 'capacity_min' in entities) and 'location' not in entities:
            return True
        
        # If query has technology but no location/capacity, it's partial
        if 'technology' in entities and 'location' not in entities and 'capacity' not in entities:
            return True
        
        # If query is very short and has limited entities
        if len(query_lower.split()) <= 3 and len(entities) <= 1:
            return True
        
        return False
    
    def _handle_special_cases(self, merged: Dict, query_lower: str, context: Dict) -> Dict:
        """Handle special query cases"""
        
        # "what are the nearest installations" - needs previous location
        if 'nearest' in query_lower and not merged.get('location'):
            if context.get('location'):
                merged['location'] = context['location']
                merged['query_type'] = 'geographic'
                merged['geo_center'] = context['location']
                merged['geo_radius'] = 30  # Default radius
        
        # "any installations" - broad search in previous location
        if re.search(r'any\s+(installations?|sites?|farms?)', query_lower):
            if context.get('location') and not merged.get('location'):
                merged['location'] = context['location']
        
        # Handle relative capacity queries
        if 'larger' in query_lower or 'bigger' in query_lower:
            if context.get('capacity'):
                merged['capacity_min'] = context['capacity'] + 50
        elif 'smaller' in query_lower:
            if context.get('capacity'):
                merged['capacity_max'] = context['capacity'] - 50
        
        return merged
    
    def _cleanup_old_sessions(self):
        """Remove sessions older than timeout"""
        now = datetime.now()
        timeout_delta = timedelta(minutes=self.timeout_minutes)
        
        expired_sessions = []
        for session_id, session_data in self.sessions.items():
            if now - session_data['last_active'] > timeout_delta:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
    
    def get_context_summary(self, session_id: str) -> str:
        """Get a human-readable summary of current context"""
        session = self.get_or_create_session(session_id)
        context = session['context']
        
        summary_parts = []
        
        if context.get('location'):
            summary_parts.append(f"Location: {context['location']}")
        
        if context.get('capacity'):
            summary_parts.append(f"Capacity: {context['capacity']}kW")
        elif context.get('capacity_min') or context.get('capacity_max'):
            if context.get('capacity_min') and context.get('capacity_max'):
                summary_parts.append(f"Capacity: {context['capacity_min']}-{context['capacity_max']}kW")
            elif context.get('capacity_min'):
                summary_parts.append(f"Capacity: >{context['capacity_min']}kW")
            else:
                summary_parts.append(f"Capacity: <{context['capacity_max']}kW")
        
        if context.get('technology'):
            summary_parts.append(f"Technology: {context['technology']}")
        
        if summary_parts:
            return "Current context: " + ", ".join(summary_parts)
        else:
            return "No active context"

# Global instance
conversation_manager = ConversationContext()

def enhance_query_with_context(session_id: str, query: str, 
                              extracted_entities: Dict, 
                              results_count: int = 0) -> Dict:
    """
    Main function to enhance query with conversational context
    
    Args:
        session_id: Unique session identifier
        query: User's current query
        extracted_entities: Entities extracted from current query
        results_count: Number of results from previous query
    
    Returns:
        Enhanced entities with context
    """
    return conversation_manager.update_context(
        session_id, query, extracted_entities, results_count
    )