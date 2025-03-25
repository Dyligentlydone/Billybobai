import sqlite3
from typing import Dict, Optional, List
import json

class ConfigService:
    def __init__(self, db_path: str = 'whys.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create voice_configs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                phone_number TEXT UNIQUE NOT NULL,
                config JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create voice_analytics table for tracking call metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                call_sid TEXT UNIQUE NOT NULL,
                from_number TEXT NOT NULL,
                duration INTEGER,
                menu_selections TEXT,
                ai_interactions INTEGER DEFAULT 0,
                recording_url TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    async def save_voice_config(self, business_id: str, config: Dict) -> bool:
        """Save or update voice configuration for a business."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if config exists for this phone number
            cursor.execute(
                'SELECT id FROM voice_configs WHERE phone_number = ?',
                (config['business']['phone'],)
            )
            existing = cursor.fetchone()

            if existing:
                # Update existing config
                cursor.execute('''
                    UPDATE voice_configs 
                    SET config = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE phone_number = ?
                ''', (json.dumps(config), config['business']['phone']))
            else:
                # Insert new config
                cursor.execute('''
                    INSERT INTO voice_configs (business_id, phone_number, config)
                    VALUES (?, ?, ?)
                ''', (business_id, config['business']['phone'], json.dumps(config)))

            conn.commit()
            return True

        except Exception as e:
            print(f"Error saving voice config: {e}")
            return False

        finally:
            conn.close()

    async def get_voice_config_by_phone(self, phone_number: str) -> Optional[Dict]:
        """Retrieve voice configuration by phone number."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                'SELECT config FROM voice_configs WHERE phone_number = ?',
                (phone_number,)
            )
            result = cursor.fetchone()

            if result:
                return json.loads(result[0])
            return None

        except Exception as e:
            print(f"Error retrieving voice config: {e}")
            return None

        finally:
            conn.close()

    async def get_voice_configs_by_business(self, business_id: str) -> List[Dict]:
        """Retrieve all voice configurations for a business."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                'SELECT config FROM voice_configs WHERE business_id = ?',
                (business_id,)
            )
            results = cursor.fetchall()

            return [json.loads(config[0]) for config in results]

        except Exception as e:
            print(f"Error retrieving voice configs: {e}")
            return []

        finally:
            conn.close()

    async def delete_voice_config(self, phone_number: str) -> bool:
        """Delete a voice configuration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                'DELETE FROM voice_configs WHERE phone_number = ?',
                (phone_number,)
            )
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error deleting voice config: {e}")
            return False

        finally:
            conn.close()

    async def log_call(
        self,
        business_id: str,
        call_sid: str,
        from_number: str,
        status: str,
        menu_selections: Optional[List[str]] = None,
        duration: Optional[int] = None,
        recording_url: Optional[str] = None,
        ai_interactions: int = 0
    ) -> bool:
        """Log call analytics data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO voice_analytics (
                    business_id, call_sid, from_number, status,
                    menu_selections, duration, recording_url, ai_interactions
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                business_id,
                call_sid,
                from_number,
                status,
                json.dumps(menu_selections) if menu_selections else None,
                duration,
                recording_url,
                ai_interactions
            ))
            conn.commit()
            return True

        except Exception as e:
            print(f"Error logging call: {e}")
            return False

        finally:
            conn.close()

    async def get_call_analytics(
        self,
        business_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve call analytics for a business."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = 'SELECT * FROM voice_analytics WHERE business_id = ?'
            params = [business_id]

            if start_date:
                query += ' AND created_at >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND created_at <= ?'
                params.append(end_date)

            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()

            return [dict(zip(columns, row)) for row in results]

        except Exception as e:
            print(f"Error retrieving call analytics: {e}")
            return []

        finally:
            conn.close()
