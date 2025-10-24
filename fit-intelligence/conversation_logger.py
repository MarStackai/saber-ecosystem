#!/usr/bin/env python3
"""
Conversation Logger for FIT Intelligence Chatbot
Captures user interactions, responses, and feedback for model improvement
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationLogger:
    """
    Comprehensive logging system for chatbot conversations
    Captures queries, responses, feedback, and performance metrics
    """
    
    def __init__(self, db_path: str = "fit_conversations.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with conversation and feedback tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    user_query TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    intent_analysis JSON,
                    data_points_returned INTEGER,
                    response_time_ms INTEGER,
                    search_type TEXT,
                    user_ip TEXT,
                    user_agent TEXT
                )
            """)
            
            # Feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    rating INTEGER, -- 1-5 star rating
                    accuracy_rating INTEGER, -- 1-5 for factual accuracy
                    usefulness_rating INTEGER, -- 1-5 for business value
                    feedback_text TEXT,
                    improvement_suggestion TEXT,
                    user_context TEXT, -- What they were trying to accomplish
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # Query patterns table for analysis
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_patterns (
                    id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL, -- 'geographic', 'technology', 'capacity', etc.
                    pattern_value TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    avg_rating REAL DEFAULT 0.0,
                    query_count INTEGER DEFAULT 1,
                    last_updated DATETIME NOT NULL
                )
            """)
            
            # Response quality metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    hallucination_detected BOOLEAN DEFAULT FALSE,
                    data_accuracy_score REAL, -- 0.0-1.0
                    response_completeness REAL, -- 0.0-1.0
                    business_relevance REAL, -- 0.0-1.0
                    follow_up_required BOOLEAN DEFAULT FALSE,
                    error_type TEXT, -- 'no_data', 'api_error', 'parsing_error', etc.
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            conn.commit()
    
    def log_conversation(self, 
                        session_id: str,
                        user_query: str, 
                        bot_response: str,
                        intent_analysis: Dict = None,
                        data_points: int = 0,
                        response_time_ms: int = 0,
                        search_type: str = None,
                        user_ip: str = None,
                        user_agent: str = None) -> str:
        """Log a complete conversation exchange"""
        
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations 
                (id, session_id, timestamp, user_query, bot_response, 
                 intent_analysis, data_points_returned, response_time_ms, 
                 search_type, user_ip, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_id, session_id, timestamp, user_query, bot_response,
                json.dumps(intent_analysis) if intent_analysis else None,
                data_points, response_time_ms, search_type, user_ip, user_agent
            ))
            conn.commit()
        
        logger.info(f"Logged conversation {conversation_id[:8]}: {len(user_query)} chars query")
        return conversation_id
    
    def log_feedback(self,
                    conversation_id: str,
                    rating: int = None,
                    accuracy_rating: int = None,
                    usefulness_rating: int = None,
                    feedback_text: str = None,
                    improvement_suggestion: str = None,
                    user_context: str = None) -> str:
        """Log user feedback for a conversation"""
        
        feedback_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback
                (id, conversation_id, timestamp, rating, accuracy_rating, 
                 usefulness_rating, feedback_text, improvement_suggestion, user_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback_id, conversation_id, timestamp, rating, accuracy_rating,
                usefulness_rating, feedback_text, improvement_suggestion, user_context
            ))
            conn.commit()
        
        logger.info(f"Logged feedback for conversation {conversation_id[:8]}: rating {rating}")
        return feedback_id
    
    def log_quality_metrics(self,
                           conversation_id: str,
                           hallucination_detected: bool = False,
                           data_accuracy_score: float = None,
                           response_completeness: float = None,
                           business_relevance: float = None,
                           follow_up_required: bool = False,
                           error_type: str = None) -> str:
        """Log automated quality metrics for a response"""
        
        metrics_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quality_metrics
                (id, conversation_id, timestamp, hallucination_detected,
                 data_accuracy_score, response_completeness, business_relevance,
                 follow_up_required, error_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics_id, conversation_id, timestamp, hallucination_detected,
                data_accuracy_score, response_completeness, business_relevance,
                follow_up_required, error_type
            ))
            conn.commit()
        
        return metrics_id
    
    def get_conversation_analytics(self, days: int = 30) -> Dict:
        """Get comprehensive analytics for conversation performance"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Basic conversation stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_conversations,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    AVG(data_points_returned) as avg_data_points,
                    AVG(response_time_ms) as avg_response_time_ms
                FROM conversations 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            
            basic_stats = cursor.fetchone()
            
            # Feedback stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_feedback,
                    AVG(rating) as avg_rating,
                    AVG(accuracy_rating) as avg_accuracy,
                    AVG(usefulness_rating) as avg_usefulness
                FROM feedback f
                JOIN conversations c ON f.conversation_id = c.id
                WHERE c.timestamp >= datetime('now', '-{} days')
            """.format(days))
            
            feedback_stats = cursor.fetchone()
            
            # Top query patterns
            cursor.execute("""
                SELECT search_type, COUNT(*) as count
                FROM conversations 
                WHERE timestamp >= datetime('now', '-{} days')
                    AND search_type IS NOT NULL
                GROUP BY search_type
                ORDER BY count DESC
                LIMIT 10
            """.format(days))
            
            search_patterns = cursor.fetchall()
            
            # Quality metrics
            cursor.execute("""
                SELECT 
                    AVG(data_accuracy_score) as avg_accuracy,
                    AVG(response_completeness) as avg_completeness,
                    AVG(business_relevance) as avg_relevance,
                    COUNT(*) FILTER (WHERE hallucination_detected = 1) as hallucinations,
                    COUNT(*) as total_quality_checks
                FROM quality_metrics qm
                JOIN conversations c ON qm.conversation_id = c.id
                WHERE c.timestamp >= datetime('now', '-{} days')
            """.format(days))
            
            quality_stats = cursor.fetchone()
            
            return {
                'period_days': days,
                'basic_stats': {
                    'total_conversations': basic_stats[0],
                    'unique_sessions': basic_stats[1],
                    'avg_data_points': round(basic_stats[2] or 0, 1),
                    'avg_response_time_ms': round(basic_stats[3] or 0, 1)
                },
                'feedback_stats': {
                    'total_feedback': feedback_stats[0],
                    'avg_rating': round(feedback_stats[1] or 0, 2),
                    'avg_accuracy': round(feedback_stats[2] or 0, 2),
                    'avg_usefulness': round(feedback_stats[3] or 0, 2)
                },
                'search_patterns': [
                    {'type': row[0], 'count': row[1]} for row in search_patterns
                ],
                'quality_stats': {
                    'avg_accuracy': round(quality_stats[0] or 0, 3),
                    'avg_completeness': round(quality_stats[1] or 0, 3),
                    'avg_relevance': round(quality_stats[2] or 0, 3),
                    'hallucination_rate': round((quality_stats[3] or 0) / max(quality_stats[4], 1) * 100, 2),
                    'total_checks': quality_stats[4]
                }
            }
    
    def get_poor_performing_queries(self, min_rating: float = 3.0, limit: int = 20) -> List[Dict]:
        """Identify queries that consistently perform poorly for improvement"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.user_query,
                    c.bot_response,
                    AVG(f.rating) as avg_rating,
                    COUNT(f.rating) as feedback_count,
                    c.intent_analysis,
                    c.data_points_returned
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
                WHERE f.rating IS NOT NULL
                GROUP BY c.user_query
                HAVING AVG(f.rating) < ? AND COUNT(f.rating) >= 2
                ORDER BY AVG(f.rating) ASC, COUNT(f.rating) DESC
                LIMIT ?
            """, (min_rating, limit))
            
            return [
                {
                    'query': row[0],
                    'avg_rating': round(row[2], 2),
                    'feedback_count': row[3],
                    'intent_analysis': json.loads(row[4]) if row[4] else {},
                    'data_points': row[5]
                }
                for row in cursor.fetchall()
            ]
    
    def export_training_data(self, min_rating: float = 4.0) -> List[Dict]:
        """Export high-quality conversations for fine-tuning"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.user_query,
                    c.bot_response,
                    c.intent_analysis,
                    AVG(f.rating) as avg_rating,
                    AVG(f.accuracy_rating) as avg_accuracy
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
                WHERE f.rating >= ?
                GROUP BY c.id
                ORDER BY AVG(f.rating) DESC, AVG(f.accuracy_rating) DESC
            """, (min_rating,))
            
            return [
                {
                    'messages': [
                        {'role': 'user', 'content': row[0]},
                        {'role': 'assistant', 'content': row[1]}
                    ],
                    'metadata': {
                        'intent': json.loads(row[2]) if row[2] else {},
                        'avg_rating': round(row[3] or 0, 2),
                        'avg_accuracy': round(row[4] or 0, 2)
                    }
                }
                for row in cursor.fetchall()
            ]

if __name__ == '__main__':
    # Test the logging system
    logger_test = ConversationLogger("test_conversations.db")
    
    # Test conversation logging
    conv_id = logger_test.log_conversation(
        session_id="test_session",
        user_query="What wind farms in Scotland need urgent PPA attention?",
        bot_response="Based on 15 sites in our database: Scotland has 3 wind farms requiring immediate PPA attention...",
        intent_analysis={'primary_focus': 'urgent_opportunities', 'technology_filter': 'Wind'},
        data_points=15,
        response_time_ms=2500,
        search_type='business_query'
    )
    
    # Test feedback logging
    logger_test.log_feedback(
        conversation_id=conv_id,
        rating=5,
        accuracy_rating=5,
        usefulness_rating=4,
        feedback_text="Very helpful for identifying PPA opportunities",
        user_context="Looking for wind farm acquisition targets"
    )
    
    # Test analytics
    analytics = logger_test.get_conversation_analytics(7)
    print("Analytics:", json.dumps(analytics, indent=2))