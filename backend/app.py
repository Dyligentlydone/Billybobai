from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from zenpy import Zenpy
import sqlite3
from dotenv import load_dotenv
from routes import auth, workflows, monitoring, sms_routes

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(workflows.bp)
    app.register_blueprint(monitoring.bp)
    app.register_blueprint(sms_routes.sms_bp)

    def get_db():
        conn = sqlite3.connect('whys.db')
        conn.row_factory = sqlite3.Row
        return conn

    def init_db():
        conn = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            conn.cursor().executescript(f.read())
        conn.commit()
        conn.close()

    @app.route('/api/analytics', methods=['GET'])
    def get_analytics():
        try:
            client_id = request.args.get('clientId')
            start_date = datetime.strptime(request.args.get('startDate'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('endDate'), '%Y-%m-%d')
            
            # Get client configuration
            client_config = get_client_config(client_id)
            
            # Initialize API clients
            twilio_client = TwilioClient(
                client_config['twilio_config']['account_sid'],
                client_config['twilio_config']['auth_token']
            )
            sendgrid_client = SendGridAPIClient(client_config['sendgrid_config']['api_key'])
            zendesk_client = Zenpy(
                client_config['zendesk_config']['subdomain'],
                client_config['zendesk_config']['email'],
                client_config['zendesk_config']['api_token']
            )
            
            # Get analytics data
            twilio_analytics = get_twilio_analytics(twilio_client, start_date, end_date)
            sendgrid_analytics = get_sendgrid_analytics(sendgrid_client, start_date, end_date)
            zendesk_analytics = get_zendesk_analytics(zendesk_client, start_date, end_date)
            
            # Calculate costs
            costs = calculate_costs(twilio_analytics, sendgrid_analytics, zendesk_analytics)
            
            return jsonify({
                'twilio': twilio_analytics,
                'sendgrid': sendgrid_analytics,
                'zendesk': zendesk_analytics,
                'costs': costs
            })
        
        except Exception as e:
            app.logger.error(f'Error fetching analytics: {str(e)}')
            return jsonify({'error': 'Failed to fetch analytics'}), 500

    def get_client_config(client_id):
        # For development, return mock configuration
        return {
            'twilio_config': {
                'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
                'auth_token': os.getenv('TWILIO_AUTH_TOKEN')
            },
            'sendgrid_config': {
                'api_key': os.getenv('SENDGRID_API_KEY')
            },
            'zendesk_config': {
                'email': os.getenv('ZENDESK_EMAIL'),
                'api_token': os.getenv('ZENDESK_API_TOKEN'),
                'subdomain': os.getenv('ZENDESK_SUBDOMAIN')
            }
        }

    def get_twilio_analytics(client, start_date, end_date):
        previous_start = start_date - timedelta(days=(end_date - start_date).days)
        
        # Get current period messages
        messages = client.messages.list(
            date_sent_after=start_date,
            date_sent_before=end_date
        )
        
        # Get previous period messages
        previous_messages = client.messages.list(
            date_sent_after=previous_start,
            date_sent_before=start_date
        )
        
        # Calculate daily metrics
        daily_messages = {}
        for msg in messages:
            date = msg.date_sent.strftime('%Y-%m-%d')
            if date not in daily_messages:
                daily_messages[date] = {'date': date, 'sms': 0, 'voice': 0}
            daily_messages[date]['sms'] += 1
        
        return {
            'totalMessages': len(messages),
            'messageChange': calculate_percentage_change(len(messages), len(previous_messages)),
            'dailyMessages': sorted(daily_messages.values(), key=lambda x: x['date'])
        }

    def get_sendgrid_analytics(client, start_date, end_date):
        previous_start = start_date - timedelta(days=(end_date - start_date).days)
        
        # Get current period stats
        stats = client.client.stats.get(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            aggregated_by='day'
        )
        
        # Get previous period stats
        previous_stats = client.client.stats.get(
            start_date=previous_start.strftime('%Y-%m-%d'),
            end_date=start_date.strftime('%Y-%m-%d'),
            aggregated_by='day'
        )
        
        total_emails = sum(day['stats'][0]['metrics']['delivered'] for day in stats)
        previous_total = sum(day['stats'][0]['metrics']['delivered'] for day in previous_stats)
        
        return {
            'totalEmails': total_emails,
            'emailChange': calculate_percentage_change(total_emails, previous_total),
            'emailMetrics': [{
                'date': day['date'],
                'delivered': day['stats'][0]['metrics']['delivered'],
                'opened': day['stats'][0]['metrics']['opens'],
                'clicked': day['stats'][0]['metrics']['clicks']
            } for day in stats]
        }

    def get_zendesk_analytics(client, start_date, end_date):
        previous_start = start_date - timedelta(days=(end_date - start_date).days)
        
        # Get current period tickets
        current_tickets = list(client.search(
            type='ticket',
            created_between=[start_date.isoformat(), end_date.isoformat()]
        ))
        
        # Get previous period tickets
        previous_tickets = list(client.search(
            type='ticket',
            created_between=[previous_start.isoformat(), start_date.isoformat()]
        ))
        
        return {
            'totalTickets': len(current_tickets),
            'ticketChange': calculate_percentage_change(len(current_tickets), len(previous_tickets)),
            'ticketsByPriority': {
                priority: len([t for t in current_tickets if getattr(t, 'priority', 'normal') == priority])
                for priority in ['urgent', 'high', 'normal', 'low']
            }
        }

    def calculate_costs(twilio_analytics, sendgrid_analytics, zendesk_analytics):
        # Cost constants
        TWILIO_SMS_COST = 0.0075  # per message
        TWILIO_VOICE_COST = 0.0085  # per minute
        SENDGRID_COST = 0.0001  # per email
        ZENDESK_COST = 0.5  # per ticket
        
        return {
            'twilio': {
                'current': twilio_analytics['totalMessages'] * TWILIO_SMS_COST,
                'previous': 0,
                'breakdown': {
                    'sms': twilio_analytics['totalMessages'] * TWILIO_SMS_COST
                }
            },
            'sendgrid': {
                'current': sendgrid_analytics['totalEmails'] * SENDGRID_COST,
                'previous': 0,
                'breakdown': {
                    'email': sendgrid_analytics['totalEmails'] * SENDGRID_COST
                }
            },
            'zendesk': {
                'current': zendesk_analytics['totalTickets'] * ZENDESK_COST,
                'previous': 0,
                'breakdown': {
                    'tickets': zendesk_analytics['totalTickets'] * ZENDESK_COST
                }
            }
        }

    def calculate_percentage_change(current, previous):
        if previous == 0:
            return 100
        return ((current - previous) / previous) * 100

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=3000)
