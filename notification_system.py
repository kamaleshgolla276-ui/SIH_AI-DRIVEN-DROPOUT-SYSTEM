# notification_system.py
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import json
import os

logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self, config_file: str = 'notification_config.json'):
        """Initialize notification system"""
        self.config = self.load_config(config_file)
        self.smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.config.get('smtp_port', 587)
        self.email = self.config.get('email', '')
        self.password = self.config.get('password', '')
        self.recipients = self.config.get('recipients', [])
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load notification configuration"""
        default_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email': '',
            'password': '',
            'recipients': ['admin@school.edu'],
            'enable_email': False,
            'enable_console': True
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Error loading config file: {e}. Using default config.")
        
        return default_config
    
    def send_alert(self, recipient: str, subject: str, message: str) -> bool:
        """Send alert via email"""
        try:
            if self.config.get('enable_console', True):
                self.send_console_alert(recipient, subject, message)
            
            if self.config.get('enable_email', False) and self.email and self.password:
                return self.send_email_alert(recipient, subject, message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False
    
    def send_console_alert(self, recipient: str, subject: str, message: str):
        """Send alert to console (for development/testing)"""
        print("\n" + "="*60)
        print("🚨 ALERT NOTIFICATION")
        print("="*60)
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print("-" * 60)
        print(message)
        print("="*60 + "\n")
        logger.info(f"Console alert sent to {recipient}")
    
    def send_email_alert(self, recipient: str, subject: str, message: str) -> bool:
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, recipient, text)
            server.quit()
            
            logger.info(f"Email alert sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_batch_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """Send multiple alerts in batch"""
        success_count = 0
        
        for alert in alerts:
            if self.send_alert(
                alert.get('recipient', 'admin@school.edu'),
                alert.get('subject', 'Student Dropout Alert'),
                alert.get('message', '')
            ):
                success_count += 1
        
        logger.info(f"Sent {success_count}/{len(alerts)} batch alerts")
        return success_count
    
    def create_alert_message(self, student_data: Dict[str, Any]) -> str:
        """Create formatted alert message"""
        message = f"""
🔴 HIGH RISK STUDENT ALERT 🔴

Student Information:
- ID: {student_data.get('student_id', 'N/A')}
- Name: {student_data.get('name', 'N/A')}
- Age: {student_data.get('age', 'N/A')}
- Gender: {student_data.get('gender', 'N/A')}

Risk Assessment:
- Dropout Probability: {student_data.get('probability', 0):.2%}
- Risk Level: {student_data.get('risk_level', 'N/A')}
- Timestamp: {student_data.get('timestamp', 'N/A')}

Academic Performance:
- Attendance Rate: {student_data.get('attendance_rate', 0):.2%}
- Average Test Score: {student_data.get('avg_test_score', 0):.1f}
- Fee Default Rate: {student_data.get('fee_default_rate', 0):.2%}

Recommended Actions:
1. Contact student immediately
2. Schedule counseling session
3. Review academic support options
4. Monitor attendance closely
5. Consider financial assistance if needed

Please take immediate action to prevent potential dropout.
        """
        return message.strip()
    
    def create_daily_summary(self, summary_data: Dict[str, Any]) -> str:
        """Create daily summary report"""
        message = f"""
📊 DAILY DROPOUT PREDICTION SUMMARY

Date: {summary_data.get('date', 'N/A')}

Statistics:
- Total Students Analyzed: {summary_data.get('total_students', 0)}
- High Risk Students: {summary_data.get('high_risk_count', 0)}
- New Alerts Generated: {summary_data.get('new_alerts', 0)}
- Interventions Recommended: {summary_data.get('interventions', 0)}

Risk Distribution:
- Green (Low Risk): {summary_data.get('green_count', 0)} ({summary_data.get('green_percentage', 0):.1f}%)
- Amber (Medium Risk): {summary_data.get('amber_count', 0)} ({summary_data.get('amber_percentage', 0):.1f}%)
- Red (High Risk): {summary_data.get('red_count', 0)} ({summary_data.get('red_percentage', 0):.1f}%)

Top Risk Factors:
{summary_data.get('top_factors', 'N/A')}

Next Steps:
- Review high-risk students
- Schedule interventions
- Update student records
- Monitor progress
        """
        return message.strip()
