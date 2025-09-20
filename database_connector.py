# database_connector.py
import pandas as pd
import sqlite3
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseConnector:
    def __init__(self, db_path: str = 'student_dropout.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create student_records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_records (
                    student_id TEXT PRIMARY KEY,
                    name TEXT,
                    gender TEXT,
                    age INTEGER,
                    socioeconomic_status TEXT,
                    previous_academic_score REAL,
                    distance_from_school_km REAL,
                    attendance_rate REAL,
                    avg_test_score REAL,
                    fee_default_rate REAL,
                    extracurricular_participation TEXT,
                    mentor_id TEXT,
                    is_active INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    prediction INTEGER,
                    probability REAL,
                    risk_level TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES student_records (student_id)
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    risk_level TEXT,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (student_id) REFERENCES student_records (student_id)
                )
            ''')
            
            self.connection.commit()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            df = pd.read_sql_query(query, self.connection, params=params)
            return df
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def insert_student_record(self, student_data: Dict[str, Any]) -> bool:
        """Insert a new student record"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO student_records 
                (student_id, name, gender, age, socioeconomic_status, 
                 previous_academic_score, distance_from_school_km, 
                 attendance_rate, avg_test_score, fee_default_rate, 
                 extracurricular_participation, mentor_id, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_data.get('student_id'),
                student_data.get('name'),
                student_data.get('gender'),
                student_data.get('age'),
                student_data.get('socioeconomic_status'),
                student_data.get('previous_academic_score'),
                student_data.get('distance_from_school_km'),
                student_data.get('attendance_rate'),
                student_data.get('avg_test_score'),
                student_data.get('fee_default_rate'),
                student_data.get('extracurricular_participation'),
                student_data.get('mentor_id'),
                student_data.get('is_active', 1)
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error inserting student record: {e}")
            return False
    
    def insert_prediction(self, prediction_data: Dict[str, Any]) -> bool:
        """Insert prediction result"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (student_id, prediction, probability, risk_level)
                VALUES (?, ?, ?, ?)
            ''', (
                prediction_data.get('student_id'),
                prediction_data.get('prediction'),
                prediction_data.get('probability'),
                prediction_data.get('risk_level')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error inserting prediction: {e}")
            return False
    
    def insert_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Insert alert"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO alerts 
                (student_id, risk_level, message)
                VALUES (?, ?, ?)
            ''', (
                alert_data.get('student_id'),
                alert_data.get('risk_level'),
                alert_data.get('message')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error inserting alert: {e}")
            return False
    
    def get_recent_predictions(self, limit: int = 100) -> pd.DataFrame:
        """Get recent predictions"""
        query = '''
            SELECT p.*, s.name, s.gender, s.age
            FROM predictions p
            JOIN student_records s ON p.student_id = s.student_id
            ORDER BY p.timestamp DESC
            LIMIT ?
        '''
        return self.execute_query(query, (limit,))
    
    def get_high_risk_students(self, threshold: float = 0.7) -> pd.DataFrame:
        """Get high-risk students"""
        query = '''
            SELECT p.*, s.name, s.gender, s.age
            FROM predictions p
            JOIN student_records s ON p.student_id = s.student_id
            WHERE p.probability > ?
            ORDER BY p.probability DESC
        '''
        return self.execute_query(query, (threshold,))
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
