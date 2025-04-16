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
    
    # Get message metrics including status and retry data
    cursor.execute("""
        SELECT 
            COUNT(*) as total_messages,
            SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_count,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
            SUM(CASE WHEN retry_attempt > 0 THEN 1 ELSE 0 END) as retried_count,
            AVG(CASE WHEN retry_attempt > 0 THEN retry_attempt ELSE 0 END) as avg_retries,
            SUM(CASE WHEN is_opted_out = 1 THEN 1 ELSE 0 END) as opt_out_count,
            AVG(CASE 
                WHEN status = 'delivered' 
                THEN ROUND((julianday(updated_at) - julianday(created_at)) * 86400)
                ELSE NULL 
            END) as avg_delivery_time
        FROM sms_messages
        WHERE business_id = ?
        AND date(created_at) BETWEEN date(?) AND date(?)
    """, (client_id, start_date, end_date))
    
    message_metrics = dict(cursor.fetchone())
    
    # Get hourly message volume and status distribution
    cursor.execute("""
        SELECT 
            strftime('%H', created_at) as hour,
            status,
            COUNT(*) as count
        FROM sms_messages
        WHERE business_id = ?
        AND date(created_at) BETWEEN date(?) AND date(?)
        GROUP BY hour, status
        ORDER BY hour, status
    """, (client_id, start_date, end_date))
    
    hourly_stats = {}
    for row in cursor.fetchall():
        hour = row[0]
        status = row[1]
        count = row[2]
        if hour not in hourly_stats:
            hourly_stats[hour] = {}
        hourly_stats[hour][status] = count
    
    # Get opt-out trends
    cursor.execute("""
        SELECT 
            date(opted_out_at) as date,
            COUNT(*) as count
        FROM opt_outs
        WHERE business_id = ?
        AND date(opted_out_at) BETWEEN date(?) AND date(?)
        GROUP BY date
        ORDER BY date
    """, (client_id, start_date, end_date))
    
    opt_out_trends = [
        {
            'date': row[0],
            'count': row[1]
        }
        for row in cursor.fetchall()
    ]
    
    # Get error distribution
    cursor.execute("""
        SELECT 
            error_code,
            COUNT(*) as count
        FROM sms_messages
        WHERE business_id = ?
        AND date(created_at) BETWEEN date(?) AND date(?)
        AND error_code IS NOT NULL
        GROUP BY error_code
        ORDER BY count DESC
        LIMIT 10
    """, (client_id, start_date, end_date))
    
    error_distribution = [
        {
            'error_code': row[0],
            'count': row[1]
        }
        for row in cursor.fetchall()
    ]
    
    return jsonify({
        'message_metrics': message_metrics,
        'hourly_stats': hourly_stats,
        'opt_out_trends': opt_out_trends,
        'error_distribution': error_distribution
    })
