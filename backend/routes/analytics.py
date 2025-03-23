from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from ..services.sms_processor import SMSProcessor
from ..utils.cost_tracking import CostTracker
from ..utils.message_quality import MessageQualityAnalyzer
from ..database import get_db

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/businesses', methods=['GET'])
def get_businesses():
    """Get list of businesses with active SMS workflows"""
    db = get_db()
    cursor = db.cursor()
    
    # Get businesses with active workflows
    cursor.execute("""
        SELECT DISTINCT b.id, b.name, 
            CASE WHEN w.status = 'active' THEN 1 ELSE 0 END as active
        FROM businesses b
        LEFT JOIN workflows w ON b.id = w.business_id
        WHERE w.type = 'sms_automation'
        ORDER BY b.name
    """)
    
    businesses = [
        {
            'id': row[0],
            'name': row[1],
            'active': bool(row[2])
        }
        for row in cursor.fetchall()
    ]
    
    return jsonify(businesses)

@analytics_bp.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for a specific business"""
    client_id = request.args.get('clientId')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    if not all([client_id, start_date, end_date]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Get message metrics
    cursor.execute("""
        SELECT 
            date(created_at) as date,
            COUNT(*) as total_messages,
            AVG(response_time) as avg_response_time,
            AVG(sentiment_score) as avg_sentiment,
            AVG(quality_score) as avg_quality
        FROM messages
        WHERE business_id = ? 
        AND date(created_at) BETWEEN ? AND ?
        GROUP BY date(created_at)
        ORDER BY date(created_at)
    """, (client_id, start_date, end_date))
    
    daily_metrics = cursor.fetchall()
    
    # Get cost data
    cursor.execute("""
        SELECT 
            date(created_at) as date,
            SUM(ai_cost) as ai_cost,
            SUM(sms_cost) as sms_cost
        FROM message_costs
        WHERE business_id = ?
        AND date(created_at) BETWEEN ? AND ?
        GROUP BY date(created_at)
        ORDER BY date(created_at)
    """, (client_id, start_date, end_date))
    
    cost_data = cursor.fetchall()
    
    # Get response types distribution
    cursor.execute("""
        SELECT 
            response_type,
            COUNT(*) as count
        FROM messages
        WHERE business_id = ?
        AND date(created_at) BETWEEN ? AND ?
        GROUP BY response_type
    """, (client_id, start_date, end_date))
    
    response_types = cursor.fetchall()
    
    # Calculate period comparisons
    days = (datetime.strptime(end_date, '%Y-%m-%d') - 
            datetime.strptime(start_date, '%Y-%m-%d')).days
    previous_start = (datetime.strptime(start_date, '%Y-%m-%d') - 
                     timedelta(days=days)).strftime('%Y-%m-%d')
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_messages,
            AVG(response_time) as avg_response_time,
            SUM(ai_cost) as ai_cost,
            SUM(sms_cost) as sms_cost
        FROM messages m
        JOIN message_costs c ON m.id = c.message_id
        WHERE m.business_id = ?
        AND date(m.created_at) BETWEEN ? AND ?
    """, (client_id, previous_start, start_date))
    
    previous_period = cursor.fetchone()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_messages,
            AVG(response_time) as avg_response_time,
            SUM(ai_cost) as ai_cost,
            SUM(sms_cost) as sms_cost
        FROM messages m
        JOIN message_costs c ON m.id = c.message_id
        WHERE m.business_id = ?
        AND date(m.created_at) BETWEEN ? AND ?
    """, (client_id, start_date, end_date))
    
    current_period = cursor.fetchone()
    
    # Calculate percentage changes
    def calc_change(current, previous):
        if not previous:
            return 0
        return ((current - previous) / previous) * 100
    
    analytics_data = {
        'sms': {
            'totalMessages': current_period[0],
            'messageChange': calc_change(current_period[0], previous_period[0]),
            'avgResponseTime': current_period[1],
            'responseTimeChange': calc_change(current_period[1], previous_period[1]),
            'aiCost': current_period[2],
            'aiCostChange': calc_change(current_period[2], previous_period[2]),
            'smsCost': current_period[3],
            'smsCostChange': calc_change(current_period[3], previous_period[3]),
            'qualityMetrics': [
                {
                    'date': row[0],
                    'sentiment': row[3],
                    'quality': row[4]
                }
                for row in daily_metrics
            ],
            'responseTypes': [
                {
                    'type': row[0],
                    'count': row[1]
                }
                for row in response_types
            ],
            'dailyCosts': [
                {
                    'date': row[0],
                    'ai': row[1],
                    'sms': row[2],
                    'total': row[1] + row[2]
                }
                for row in cost_data
            ]
        }
    }
    
    return jsonify(analytics_data)
