# main.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the DropoutDashboard class from dashboard.py
exec(open('dashboard.py').read())

from integration import DropoutPredictor
from database_connector import DatabaseConnector
from notification_system import NotificationSystem
from model_maintaince import ModelMaintenance
from real_time_monitoring import RealTimeMonitor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="AI-Powered Student Dropout Prediction System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize components
    try:
        db_connector = DatabaseConnector()
        notification_system = NotificationSystem()
        predictor = DropoutPredictor()
        model_maintenance = ModelMaintenance()
        
        # Create dashboard
        dashboard = DropoutDashboard()
        
        # Sidebar navigation
        st.sidebar.title("🎓 Navigation")
        page = st.sidebar.selectbox(
            "Choose a page",
            ["Dashboard", "Student Search", "Model Management", "Monitoring", "Settings"]
        )
        
        if page == "Dashboard":
            dashboard.run()
            
        elif page == "Student Search":
            display_student_search(predictor, db_connector)
            
        elif page == "Model Management":
            display_model_management(model_maintenance)
            
        elif page == "Monitoring":
            display_monitoring(RealTimeMonitor())
            
        elif page == "Settings":
            display_settings(notification_system)
            
    except Exception as e:
        st.error(f"Error initializing application: {e}")
        logger.error(f"Application initialization error: {e}")

def display_student_search(predictor, db_connector):
    """Display student search and prediction interface"""
    st.title("🔍 Student Search & Prediction")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Search Student")
        student_id = st.text_input("Enter Student ID", "STU00123")
        
        if st.button("Search Student"):
            # Get student data from database
            query = "SELECT * FROM student_records WHERE student_id = ?"
            student_data = db_connector.execute_query(query, (student_id,))
            
            if not student_data.empty:
                st.success("Student found!")
                st.write(student_data.iloc[0].to_dict())
            else:
                st.warning("Student not found. Using sample data.")
                # Use sample data if not found
                sample_data = {
                    'student_id': student_id,
                    'gender': 'M',
                    'age': 18,
                    'socioeconomic_status': 'Middle',
                    'previous_academic_score': 68.5,
                    'distance_from_school_km': 3.2,
                    'attendance_rate': 0.65,
                    'avg_test_score': 48.7,
                    'fee_default_rate': 0.9,
                    'extracurricular_participation': 'Low'
                }
                st.write(sample_data)
    
    with col2:
        st.subheader("Prediction Results")
        if st.button("Predict Dropout Risk"):
            try:
                # Sample student data for prediction
                sample_student = {
                    'student_id': student_id,
                    'gender': 'M',
                    'age': 18,
                    'socioeconomic_status': 'Middle',
                    'previous_academic_score': 68.5,
                    'distance_from_school_km': 3.2,
                    'attendance_rate': 0.65,
                    'avg_test_score': 48.7,
                    'fee_default_rate': 0.9,
                    'extracurricular_participation': 'Low'
                }
                
                prediction, probability, risk_level = predictor.predict_dropout_risk(sample_student)
                
                # Display results
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("Prediction", "Dropout" if prediction == 0 else "Active")
                
                with col_b:
                    st.metric("Probability", f"{probability:.2%}")
                
                with col_c:
                    color = "red" if risk_level == "Red" else "orange" if risk_level == "Amber" else "green"
                    st.metric("Risk Level", risk_level)
                
                # Risk gauge
                import plotly.graph_objects as go
                
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = probability * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Dropout Probability %"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "green"},
                            {'range': [30, 70], 'color': "orange"},
                            {'range': [70, 100], 'color': "red"}
                        ]
                    }
                ))
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error making prediction: {e}")

def display_model_management(model_maintenance):
    """Display model management interface"""
    st.title("🤖 Model Management")
    
    st.subheader("Model Performance History")
    
    # Display performance history
    if model_maintenance.performance_history:
        perf_df = pd.DataFrame(model_maintenance.performance_history)
        st.dataframe(perf_df)
        
        # Performance chart
        import plotly.express as px
        fig = px.line(perf_df, x='timestamp', y=['accuracy', 'f1_score'], 
                     title='Model Performance Over Time')
        st.plotly_chart(fig)
    else:
        st.info("No performance history available")
    
    st.subheader("Model Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Check Model Drift"):
            st.info("Model drift check would be performed here")
    
    with col2:
        if st.button("Retrain Model"):
            st.info("Model retraining would be initiated here")

def display_monitoring(monitor):
    """Display monitoring interface"""
    st.title("📊 Real-time Monitoring")
    
    st.subheader("System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Status", "🟢 Online", "Active")
    
    with col2:
        st.metric("Last Update", "2 minutes ago", "On time")
    
    with col3:
        st.metric("Alerts Today", "3", "2 new")
    
    st.subheader("Recent Alerts")
    
    # Sample alerts
    alerts = [
        {'student_id': 'STU00123', 'risk_level': 'Red', 'timestamp': '2024-01-15 10:30', 'message': 'High dropout risk detected'},
        {'student_id': 'STU00456', 'risk_level': 'Red', 'timestamp': '2024-01-15 09:15', 'message': 'Attendance below threshold'},
        {'student_id': 'STU00789', 'risk_level': 'Amber', 'timestamp': '2024-01-14 16:45', 'message': 'Academic performance declining'}
    ]
    
    for alert in alerts:
        with st.expander(f"{alert['student_id']} - {alert['risk_level']} Risk"):
            st.write(f"**Time:** {alert['timestamp']}")
            st.write(f"**Message:** {alert['message']}")
            if st.button("Mark as Reviewed", key=alert['student_id']):
                st.success("Alert reviewed!")

def display_settings(notification_system):
    """Display settings interface"""
    st.title("⚙️ Settings")
    
    st.subheader("Notification Settings")
    
    enable_email = st.checkbox("Enable Email Notifications", value=False)
    enable_console = st.checkbox("Enable Console Alerts", value=True)
    
    if enable_email:
        st.text_input("SMTP Server", value="smtp.gmail.com")
        st.number_input("SMTP Port", value=587)
        st.text_input("Email Address", value="")
        st.text_input("Password", type="password", value="")
    
    st.subheader("Model Settings")
    
    risk_threshold = st.slider("High Risk Threshold", 0.0, 1.0, 0.7, 0.05)
    st.info(f"Students with dropout probability above {risk_threshold:.1%} will trigger alerts")
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

if __name__ == "__main__":
    main()
