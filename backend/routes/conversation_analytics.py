from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app.models.message import Message, MessageDirection, CustomerSentiment
from database import get_db
from utils.message_quality import analyze_conversation_topic
import logging

conversation_bp = Blueprint('conversation_bp', __name__)

@conversation_bp.route('/api/analytics/conversations/<workflow_id>', methods=['GET'])
def get_conversations(workflow_id):
    """Get conversations for a workflow with pagination"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    topic = request.args.get('topic')
    sentiment = request.args.get('sentiment')
    
    query = Message.query.filter_by(
        workflow_id=workflow_id,
        is_first_in_conversation=True
    )
    
    # Apply filters
    if start_date:
        query = query.filter(Message.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Message.created_at <= datetime.fromisoformat(end_date))
    if topic:
        query = query.filter(Message.topic == topic)
    if sentiment:
        query = query.filter(Message.customer_sentiment == sentiment)
        
    # Order by most recent first
    query = query.order_by(desc(Message.created_at))
    
    # Paginate results
    conversations = query.paginate(page=page, per_page=per_page)
    
    results = []
    for msg in conversations.items:
        # Get all messages in conversation
        thread = Message.query.filter_by(
            conversation_id=msg.conversation_id
        ).order_by(Message.created_at).all()
        
        # Calculate conversation metrics
        response_times = []
        last_time = None
        for m in thread:
            if m.direction == MessageDirection.INBOUND and last_time:
                response_times.append((m.created_at - last_time).total_seconds())
            last_time = m.created_at
            
        results.append({
            'conversation_id': msg.conversation_id,
            'started_at': msg.created_at.isoformat(),
            'phone_number': msg.phone_number,
            'topic': msg.topic,
            'sentiment': msg.customer_sentiment.value if msg.customer_sentiment else None,
            'message_count': len(thread),
            'avg_response_time': sum(response_times) / len(response_times) if response_times else None,
            'messages': [{
                'id': m.id,
                'direction': m.direction.value,
                'content': m.content,
                'created_at': m.created_at.isoformat(),
                'ai_confidence': m.ai_confidence,
                'template_used': m.template_used
            } for m in thread]
        })
    
    return jsonify({
        'conversations': results,
        'total': conversations.total,
        'pages': conversations.pages,
        'current_page': conversations.page
    })

@conversation_bp.route('/api/analytics/conversations/metrics/<workflow_id>', methods=['GET'])
def get_conversation_metrics(workflow_id):
    """Get aggregated conversation metrics"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    base_query = Message.query.filter_by(workflow_id=workflow_id)
    if start_date:
        base_query = base_query.filter(Message.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        base_query = base_query.filter(Message.created_at <= datetime.fromisoformat(end_date))
    
    # Get hourly message counts
    hourly_counts = (
        base_query
        .with_entities(
            func.date_trunc('hour', Message.created_at).label('hour'),
            func.count().label('count')
        )
        .group_by('hour')
        .order_by('hour')
        .all()
    )
    
    # Get topic distribution
    topics = (
        base_query
        .filter(Message.topic.isnot(None))
        .with_entities(Message.topic, func.count().label('count'))
        .group_by(Message.topic)
        .order_by(desc('count'))
        .limit(10)
        .all()
    )
    
    # Calculate response time stats
    response_times = (
        base_query
        .filter(Message.response_time.isnot(None))
        .with_entities(
            func.avg(Message.response_time).label('avg'),
            func.min(Message.response_time).label('min'),
            func.max(Message.response_time).label('max')
        )
        .first()
    )
    
    return jsonify({
        'hourly_activity': [{
            'hour': h.hour.isoformat(),
            'count': h.count
        } for h in hourly_counts],
        'topics': [{
            'topic': t.topic,
            'count': t.count
        } for t in topics],
        'response_times': {
            'average': float(response_times.avg) if response_times.avg else None,
            'minimum': float(response_times.min) if response_times.min else None,
            'maximum': float(response_times.max) if response_times.max else None
        }
    })
