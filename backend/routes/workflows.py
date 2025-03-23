from flask import Blueprint, request, jsonify
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Optional

bp = Blueprint('workflows', __name__)

def get_db():
    """Get database connection"""
    conn = sqlite3.connect('whys.db')
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create a new workflow with business configuration"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['business_id', 'workflow_id', 'name', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # Start transaction
            cursor.execute('BEGIN')
            
            # Insert workflow
            cursor.execute("""
                INSERT INTO workflows (id, client_id, name, type, actions)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['workflow_id'],
                data['business_id'],
                data['name'],
                data['type'],
                json.dumps(data.get('actions', {}))
            ))
            
            # Insert business configuration
            cursor.execute("""
                INSERT INTO business_configs (
                    business_id, workflow_id, phone_number, tone, context,
                    brand_voice, ai_model, max_response_tokens, temperature,
                    fallback_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['business_id'],
                data['workflow_id'],
                data['twilio']['phoneNumber'],
                data['brandTone'].get('voiceType', 'professional'),
                json.dumps(data.get('aiTraining', {})),
                data['brandTone'].get('brandVoice'),
                data['ai'].get('model', 'gpt-4'),
                data['ai'].get('maxTokens', 300),
                data['ai'].get('temperature', 0.7),
                data.get('fallbackMessage')
            ))
            
            # Commit transaction
            cursor.execute('COMMIT')
            
            logging.info(f"Created workflow {data['workflow_id']} for business {data['business_id']}")
            
            return jsonify({
                'status': 'success',
                'workflow_id': data['workflow_id']
            })
            
        except Exception as e:
            # Rollback on error
            cursor.execute('ROLLBACK')
            raise e
            
    except Exception as e:
        logging.error(f"Error creating workflow: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@bp.route('/api/workflows/<workflow_id>', methods=['PUT'])
def update_workflow(workflow_id: str):
    """Update an existing workflow and its business configuration"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # Start transaction
            cursor.execute('BEGIN')
            
            # Update workflow if it exists
            cursor.execute("""
                UPDATE workflows 
                SET name = ?,
                    type = ?,
                    actions = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data['name'],
                data['type'],
                json.dumps(data.get('actions', {})),
                workflow_id
            ))
            
            # Update business configuration
            cursor.execute("""
                UPDATE business_configs 
                SET phone_number = ?,
                    tone = ?,
                    context = ?,
                    brand_voice = ?,
                    ai_model = ?,
                    max_response_tokens = ?,
                    temperature = ?,
                    fallback_message = ?
                WHERE workflow_id = ?
            """, (
                data['twilio']['phoneNumber'],
                data['brandTone'].get('voiceType', 'professional'),
                json.dumps(data.get('aiTraining', {})),
                data['brandTone'].get('brandVoice'),
                data['ai'].get('model', 'gpt-4'),
                data['ai'].get('maxTokens', 300),
                data['ai'].get('temperature', 0.7),
                data.get('fallbackMessage'),
                workflow_id
            ))
            
            # Commit transaction
            cursor.execute('COMMIT')
            
            logging.info(f"Updated workflow {workflow_id}")
            
            return jsonify({
                'status': 'success',
                'workflow_id': workflow_id
            })
            
        except Exception as e:
            # Rollback on error
            cursor.execute('ROLLBACK')
            raise e
            
    except Exception as e:
        logging.error(f"Error updating workflow: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@bp.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id: str):
    """Get workflow and its business configuration"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get workflow
        cursor.execute("""
            SELECT w.*, bc.*
            FROM workflows w
            LEFT JOIN business_configs bc ON w.id = bc.workflow_id
            WHERE w.id = ?
        """, (workflow_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Workflow not found'}), 404
        
        # Convert row to dict and parse JSON fields
        result = dict(row)
        result['actions'] = json.loads(result['actions'])
        result['context'] = json.loads(result['context'])
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting workflow: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@bp.route('/api/workflows', methods=['GET'])
def list_workflows():
    """List all workflows for a business"""
    try:
        business_id = request.args.get('businessId')
        if not business_id:
            return jsonify({'error': 'Missing businessId parameter'}), 400
            
        conn = get_db()
        cursor = conn.cursor()
        
        # Get workflows
        cursor.execute("""
            SELECT w.*, bc.*
            FROM workflows w
            LEFT JOIN business_configs bc ON w.id = bc.workflow_id
            WHERE w.client_id = ?
            ORDER BY w.created_at DESC
        """, (business_id,))
        
        rows = cursor.fetchall()
        
        # Convert rows to dicts and parse JSON fields
        results = []
        for row in rows:
            result = dict(row)
            result['actions'] = json.loads(result['actions'])
            result['context'] = json.loads(result['context'])
            results.append(result)
        
        return jsonify(results)
        
    except Exception as e:
        logging.error(f"Error listing workflows: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@bp.route('/api/workflows/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id: str):
    """Delete a workflow and its business configuration"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # Start transaction
            cursor.execute('BEGIN')
            
            # Delete workflow (business_config will be deleted by CASCADE)
            cursor.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))
            
            if cursor.rowcount == 0:
                cursor.execute('ROLLBACK')
                return jsonify({'error': 'Workflow not found'}), 404
            
            # Commit transaction
            cursor.execute('COMMIT')
            
            logging.info(f"Deleted workflow {workflow_id}")
            
            return jsonify({'status': 'success'})
            
        except Exception as e:
            # Rollback on error
            cursor.execute('ROLLBACK')
            raise e
            
    except Exception as e:
        logging.error(f"Error deleting workflow: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()
