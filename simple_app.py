# simple_app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import os

# Set page config
st.set_page_config(
    page_title="AI-Powered Student Dropout Prediction System",
    page_icon="🎓",
    layout="wide"
)

def create_database():
    """Create database and tables"""
    conn = sqlite3.connect('student_dropout.db')
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()

def generate_sample_data(n_students=100):
    """Generate sample student data"""
    student_ids = [f'STU{i:05d}' for i in range(1, n_students+1)]
    
    data = {
        'student_id': student_ids,
        'name': [f'Student_{i}' for i in range(1, n_students+1)],
        'gender': np.random.choice(['M', 'F'], size=n_students, p=[0.55, 0.45]),
        'age': np.random.randint(16, 21, size=n_students),
        'socioeconomic_status': np.random.choice(['Low', 'Middle', 'High'], size=n_students, p=[0.3, 0.5, 0.2]),
        'previous_academic_score': np.random.normal(75, 15, n_students),
        'distance_from_school_km': np.random.exponential(5, n_students),
        'attendance_rate': np.random.normal(0.85, 0.15, n_students),
        'avg_test_score': np.random.normal(65, 20, n_students),
        'fee_default_rate': np.random.uniform(0, 1, n_students),
        'extracurricular_participation': np.random.choice(['None', 'Low', 'Medium', 'High'],
                                                         size=n_students, p=[0.4, 0.3, 0.2, 0.1]),
        'mentor_id': [f'MENT{np.random.randint(1, 51):03d}' for _ in range(n_students)],
    }
    
    df = pd.DataFrame(data)
    
    # Create target variable
    df['is_active'] = 1
    dropout_conditions = (
        (df['attendance_rate'] < 0.7) |
        (df['avg_test_score'] < 50) |
        (df['fee_default_rate'] > 0.8) |
        (df['socioeconomic_status'] == 'Low') |
        (df['distance_from_school_km'] > 10)
    )
    df.loc[dropout_conditions, 'is_active'] = 0
    
    return df

def simple_dropout_prediction(student_data):
    """Simple dropout prediction based on rules"""
    risk_score = 0
    
    # Attendance factor
    if student_data['attendance_rate'] < 0.7:
        risk_score += 0.3
    elif student_data['attendance_rate'] < 0.8:
        risk_score += 0.1
    
    # Academic performance factor
    if student_data['avg_test_score'] < 50:
        risk_score += 0.3
    elif student_data['avg_test_score'] < 60:
        risk_score += 0.1
    
    # Financial factor
    if student_data['fee_default_rate'] > 0.8:
        risk_score += 0.2
    elif student_data['fee_default_rate'] > 0.5:
        risk_score += 0.1
    
    # Socioeconomic factor
    if student_data['socioeconomic_status'] == 'Low':
        risk_score += 0.1
    
    # Distance factor
    if student_data['distance_from_school_km'] > 10:
        risk_score += 0.1
    
    # Determine risk level
    if risk_score < 0.3:
        risk_level = "Green"
    elif risk_score < 0.7:
        risk_level = "Amber"
    else:
        risk_level = "Red"
    
    return risk_score, risk_level

def main():
    """Main application"""
    st.title("🎓 AI-Powered Student Dropout Prediction System")
    
    # Initialize database
    create_database()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Student Search", "Data Management"])
    
    if page == "Dashboard":
        display_dashboard()
    elif page == "Student Search":
        display_student_search()
    elif page == "Data Management":
        display_data_management()

def display_dashboard():
    """Display main dashboard"""
    st.subheader("📊 System Overview")
    
    # Sample metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", "1,000", "5%")
    with col2:
        st.metric("At Risk Students", "150", "8%")
    with col3:
        st.metric("Interventions", "23", "12%")
    with col4:
        st.metric("Success Rate", "78%", "5%")
    
    # Risk distribution
    st.subheader("📈 Risk Distribution")
    
    risk_data = pd.DataFrame({
        'Risk Level': ['Green', 'Amber', 'Red'],
        'Count': [700, 150, 150],
        'Percentage': [70, 15, 15]
    })
    
    # Simple bar chart
    st.bar_chart(risk_data.set_index('Risk Level')['Count'])
    
    # Recent alerts
    st.subheader("⚠️ Recent Alerts")
    
    alerts = [
        {'student_id': 'STU00123', 'risk_level': 'Red', 'timestamp': '2024-01-15 10:30'},
        {'student_id': 'STU00456', 'risk_level': 'Red', 'timestamp': '2024-01-15 09:15'},
        {'student_id': 'STU00789', 'risk_level': 'Amber', 'timestamp': '2024-01-14 16:45'}
    ]
    
    for alert in alerts:
        with st.expander(f"{alert['student_id']} - {alert['risk_level']} Risk"):
            st.write(f"Alert Time: {alert['timestamp']}")
            st.write("Recommended Actions: Contact student, Schedule counseling")

def display_student_search():
    """Display student search interface"""
    st.subheader("🔍 Student Search & Prediction")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        student_id = st.text_input("Enter Student ID", "STU00123")
        
        if st.button("Search Student"):
            # Generate sample student data
            sample_student = {
                'student_id': student_id,
                'name': f'Student_{student_id}',
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
            
            st.write("**Student Information**")
            for key, value in sample_student.items():
                st.write(f"{key}: {value}")
    
    with col2:
        st.subheader("Prediction Results")
        
        if st.button("Predict Dropout Risk"):
            # Sample student data
            sample_student = {
                'student_id': 'STU00123',
                'attendance_rate': 0.65,
                'avg_test_score': 48.7,
                'fee_default_rate': 0.9,
                'socioeconomic_status': 'Low',
                'distance_from_school_km': 12.5
            }
            
            risk_score, risk_level = simple_dropout_prediction(sample_student)
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Risk Score", f"{risk_score:.2f}")
            
            with col_b:
                st.metric("Risk Level", risk_level)
            
            with col_c:
                st.metric("Probability", f"{risk_score:.1%}")
            
            # Risk gauge (simple text representation)
            st.subheader("Risk Assessment")
            if risk_level == "Red":
                st.error("🔴 HIGH RISK - Immediate intervention required")
            elif risk_level == "Amber":
                st.warning("🟡 MEDIUM RISK - Monitor closely")
            else:
                st.success("🟢 LOW RISK - Continue monitoring")

def display_data_management():
    """Display data management interface"""
    st.subheader("📊 Data Management")
    
    if st.button("Generate Sample Data"):
        with st.spinner("Generating sample data..."):
            df = generate_sample_data(100)
            
            # Save to database
            conn = sqlite3.connect('student_dropout.db')
            df.to_sql('student_records', conn, if_exists='replace', index=False)
            conn.close()
            
            st.success(f"Generated {len(df)} student records!")
            
            # Display sample data
            st.subheader("Sample Data Preview")
            st.dataframe(df.head(10))
            
            # Display statistics
            st.subheader("Data Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Dropout Rate:**", f"{(1 - df['is_active'].mean()):.1%}")
                st.write("**Average Age:**", f"{df['age'].mean():.1f}")
                st.write("**Average Attendance:**", f"{df['attendance_rate'].mean():.1%}")
            
            with col2:
                st.write("**Gender Distribution:**")
                st.write(df['gender'].value_counts())
                st.write("**Socioeconomic Status:**")
                st.write(df['socioeconomic_status'].value_counts())

if __name__ == "__main__":
    main()
