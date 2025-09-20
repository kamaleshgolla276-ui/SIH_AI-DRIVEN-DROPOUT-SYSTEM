# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging
from integration import DropoutPredictor
from database_connector import DatabaseConnector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DropoutDashboard:
    def __init__(self):
        try:
            self.predictor = DropoutPredictor()
            self.db_connector = DatabaseConnector()
            logger.info("Dashboard initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing dashboard: {e}")
            st.error(f"Error initializing dashboard: {e}")
            self.predictor = None
            self.db_connector = None
        
        st.set_page_config(page_title="Student Dropout Prediction", layout="wide")
    
    def display_overview(self):
        """Display dashboard overview"""
        st.title("🎓 AI-Powered Student Dropout Prediction System")
        
        # Get real data from database
        try:
            if self.db_connector:
                # Get total students
                total_query = "SELECT COUNT(*) as total FROM student_records"
                total_result = self.db_connector.execute_query(total_query)
                total_students = total_result.iloc[0]['total'] if not total_result.empty else 0
                
                # Get at-risk students (assuming is_active = 0 means at risk)
                at_risk_query = "SELECT COUNT(*) as at_risk FROM student_records WHERE is_active = 0"
                at_risk_result = self.db_connector.execute_query(at_risk_query)
                at_risk_students = at_risk_result.iloc[0]['at_risk'] if not at_risk_result.empty else 0
                
                # Calculate percentages
                at_risk_percentage = (at_risk_students / total_students * 100) if total_students > 0 else 0
                success_rate = ((total_students - at_risk_students) / total_students * 100) if total_students > 0 else 0
                
            else:
                # Fallback to sample data
                total_students = 1000
                at_risk_students = 150
                at_risk_percentage = 15
                success_rate = 85
                
        except Exception as e:
            logger.error(f"Error fetching overview data: {e}")
            # Fallback to sample data
            total_students = 1000
            at_risk_students = 150
            at_risk_percentage = 15
            success_rate = 85
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", f"{total_students:,}", f"{at_risk_percentage:.1f}%")
        with col2:
            st.metric("At Risk Students", f"{at_risk_students:,}", f"{at_risk_percentage:.1f}%")
        with col3:
            st.metric("Interventions", "23", "12%")
        with col4:
            st.metric("Success Rate", f"{success_rate:.1f}%", "5%")
    
    def display_risk_distribution(self):
        """Display risk distribution chart"""
        st.subheader("📊 Risk Distribution")
        
        try:
            if self.db_connector:
                # Get real data from database
                query = """
                SELECT 
                    CASE 
                        WHEN is_active = 1 THEN 'Green'
                        WHEN attendance_rate > 0.7 AND avg_test_score > 60 THEN 'Amber'
                        ELSE 'Red'
                    END as risk_level,
                    COUNT(*) as count
                FROM student_records 
                GROUP BY risk_level
                """
                result = self.db_connector.execute_query(query)
                
                if not result.empty:
                    risk_data = result
                    total = risk_data['count'].sum()
                    risk_data['percentage'] = (risk_data['count'] / total * 100).round(1)
                else:
                    # Fallback to sample data
                    risk_data = pd.DataFrame({
                        'risk_level': ['Green', 'Amber', 'Red'],
                        'count': [700, 150, 150],
                        'percentage': [70, 15, 15]
                    })
            else:
                # Fallback to sample data
                risk_data = pd.DataFrame({
                    'risk_level': ['Green', 'Amber', 'Red'],
                    'count': [700, 150, 150],
                    'percentage': [70, 15, 15]
                })
                
        except Exception as e:
            logger.error(f"Error fetching risk distribution data: {e}")
            # Fallback to sample data
            risk_data = pd.DataFrame({
                'risk_level': ['Green', 'Amber', 'Red'],
                'count': [700, 150, 150],
                'percentage': [70, 15, 15]
            })
        
        # Create pie chart
        fig = px.pie(risk_data, values='count', names='risk_level', 
                     title='Student Risk Level Distribution',
                     color_discrete_map={'Green': '#2E8B57', 'Amber': '#FF8C00', 'Red': '#DC143C'})
        
        # Add percentage labels
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display summary table
        st.subheader("Risk Level Summary")
        st.dataframe(risk_data, use_container_width=True)
    
    def display_student_search(self):
        """Display student search and details"""
        st.subheader("🔍 Student Search")
        
        student_id = st.text_input("Enter Student ID", "STU00123")
        
        if st.button("Search"):
            try:
                if self.db_connector:
                    # Fetch student data from database
                    query = "SELECT * FROM student_records WHERE student_id = ?"
                    result = self.db_connector.execute_query(query, (student_id,))
                    
                    if not result.empty:
                        student_data = result.iloc[0].to_dict()
                        
                        # Make prediction if predictor is available
                        if self.predictor:
                            try:
                                # Prepare data for prediction
                                prediction_data = {
                                    'student_id': student_data['student_id'],
                                    'gender': student_data['gender'],
                                    'age': student_data['age'],
                                    'socioeconomic_status': student_data['socioeconomic_status'],
                                    'previous_academic_score': student_data['previous_academic_score'],
                                    'distance_from_school_km': student_data['distance_from_school_km'],
                                    'attendance_rate': student_data['attendance_rate'],
                                    'avg_test_score': student_data['avg_test_score'],
                                    'fee_default_rate': student_data['fee_default_rate'],
                                    'extracurricular_participation': student_data['extracurricular_participation']
                                }
                                
                                prediction, probability, risk_level = self.predictor.predict_dropout_risk(prediction_data)
                                
                            except Exception as e:
                                logger.error(f"Error making prediction: {e}")
                                # Fallback to simple risk assessment
                                if student_data['attendance_rate'] < 0.7 or student_data['avg_test_score'] < 50:
                                    risk_level = "Red"
                                    probability = 0.8
                                elif student_data['attendance_rate'] < 0.8 or student_data['avg_test_score'] < 60:
                                    risk_level = "Amber"
                                    probability = 0.5
                                else:
                                    risk_level = "Green"
                                    probability = 0.2
                        else:
                            # Simple risk assessment without ML model
                            if student_data['attendance_rate'] < 0.7 or student_data['avg_test_score'] < 50:
                                risk_level = "Red"
                                probability = 0.8
                            elif student_data['attendance_rate'] < 0.8 or student_data['avg_test_score'] < 60:
                                risk_level = "Amber"
                                probability = 0.5
                            else:
                                risk_level = "Green"
                                probability = 0.2
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Student Information**")
                            st.write(f"**Name:** {student_data.get('name', 'N/A')}")
                            st.write(f"**Age:** {student_data.get('age', 'N/A')}")
                            st.write(f"**Gender:** {student_data.get('gender', 'N/A')}")
                            st.write(f"**Socioeconomic Status:** {student_data.get('socioeconomic_status', 'N/A')}")
                            st.write(f"**Attendance Rate:** {student_data.get('attendance_rate', 0):.1%}")
                            st.write(f"**Average Test Score:** {student_data.get('avg_test_score', 0):.1f}")
                            st.write(f"**Fee Default Rate:** {student_data.get('fee_default_rate', 0):.1%}")
                            
                        with col2:
                            st.write("**Risk Assessment**")
                            
                            # Risk gauge chart
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
                            
                            # Risk level indicator
                            if risk_level == "Red":
                                st.error(f"🔴 HIGH RISK - {probability:.1%} probability of dropout")
                            elif risk_level == "Amber":
                                st.warning(f"🟡 MEDIUM RISK - {probability:.1%} probability of dropout")
                            else:
                                st.success(f"🟢 LOW RISK - {probability:.1%} probability of dropout")
                    else:
                        st.warning(f"Student {student_id} not found in database")
                        
                else:
                    st.error("Database connection not available")
                    
            except Exception as e:
                logger.error(f"Error in student search: {e}")
                st.error(f"Error searching for student: {e}")
    
    def display_alerts(self):
        """Display recent alerts"""
        st.subheader("⚠️ Recent Alerts")
        
        try:
            if self.db_connector:
                # Get high-risk students from database
                query = """
                SELECT student_id, name, attendance_rate, avg_test_score, fee_default_rate,
                       CASE 
                           WHEN attendance_rate < 0.7 OR avg_test_score < 50 THEN 'Red'
                           WHEN attendance_rate < 0.8 OR avg_test_score < 60 THEN 'Amber'
                           ELSE 'Green'
                       END as risk_level,
                       last_updated as timestamp
                FROM student_records 
                WHERE attendance_rate < 0.8 OR avg_test_score < 60
                ORDER BY attendance_rate ASC, avg_test_score ASC
                LIMIT 10
                """
                result = self.db_connector.execute_query(query)
                
                if not result.empty:
                    alerts = result.to_dict('records')
                else:
                    # Fallback to sample data
                    alerts = [
                        {'student_id': 'STU00123', 'risk_level': 'Red', 'timestamp': '2024-01-15 10:30'},
                        {'student_id': 'STU00456', 'risk_level': 'Red', 'timestamp': '2024-01-15 09:15'},
                        {'student_id': 'STU00789', 'risk_level': 'Amber', 'timestamp': '2024-01-14 16:45'}
                    ]
            else:
                # Fallback to sample data
                alerts = [
                    {'student_id': 'STU00123', 'risk_level': 'Red', 'timestamp': '2024-01-15 10:30'},
                    {'student_id': 'STU00456', 'risk_level': 'Red', 'timestamp': '2024-01-15 09:15'},
                    {'student_id': 'STU00789', 'risk_level': 'Amber', 'timestamp': '2024-01-14 16:45'}
                ]
                
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            # Fallback to sample data
            alerts = [
                {'student_id': 'STU00123', 'risk_level': 'Red', 'timestamp': '2024-01-15 10:30'},
                {'student_id': 'STU00456', 'risk_level': 'Red', 'timestamp': '2024-01-15 09:15'},
                {'student_id': 'STU00789', 'risk_level': 'Amber', 'timestamp': '2024-01-14 16:45'}
            ]
        
        if not alerts:
            st.info("No alerts at this time")
            return
        
        for i, alert in enumerate(alerts):
            with st.expander(f"{alert['student_id']} - {alert['risk_level']} Risk"):
                st.write(f"**Student:** {alert.get('name', 'N/A')}")
                st.write(f"**Alert Time:** {alert['timestamp']}")
                
                if 'attendance_rate' in alert:
                    st.write(f"**Attendance Rate:** {alert['attendance_rate']:.1%}")
                if 'avg_test_score' in alert:
                    st.write(f"**Average Test Score:** {alert['avg_test_score']:.1f}")
                if 'fee_default_rate' in alert:
                    st.write(f"**Fee Default Rate:** {alert['fee_default_rate']:.1%}")
                
                st.write("**Recommended Actions:**")
                if alert['risk_level'] == 'Red':
                    st.write("- 🚨 Immediate intervention required")
                    st.write("- Contact student and parents")
                    st.write("- Schedule emergency counseling")
                    st.write("- Review academic support options")
                elif alert['risk_level'] == 'Amber':
                    st.write("- Monitor closely")
                    st.write("- Schedule regular check-ins")
                    st.write("- Provide additional support")
                else:
                    st.write("- Continue monitoring")
                    st.write("- Maintain current support level")
                
                if st.button("Mark as Reviewed", key=f"alert_{i}_{alert['student_id']}"):
                    st.success("Alert reviewed!")
    
    def run(self):
        """Run the dashboard"""
        # Add refresh button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        
        self.display_overview()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.display_risk_distribution()
        
        with col2:
            self.display_alerts()
        
        self.display_student_search()
        
        # Add footer
        st.markdown("---")
        st.markdown("**AI-Powered Student Dropout Prediction System** | Built with Streamlit")

# Run the dashboard
if __name__ == "__main__":
    dashboard = DropoutDashboard()
    dashboard.run()