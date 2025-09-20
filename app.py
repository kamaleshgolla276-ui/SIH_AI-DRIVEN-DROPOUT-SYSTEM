# app.py - Main Streamlit application for deployment
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="AI-Powered Student Dropout Prediction System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_database():
    """Create database and tables if they don't exist"""
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

def generate_sample_data(n_students=1000):
    """Generate sample student data"""
    np.random.seed(42)  # For reproducible results
    
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

def get_database_stats():
    """Get statistics from database"""
    try:
        conn = sqlite3.connect('student_dropout.db')
        
        # Get total students
        total_query = "SELECT COUNT(*) as total FROM student_records"
        total_result = pd.read_sql_query(total_query, conn)
        total_students = total_result.iloc[0]['total'] if not total_result.empty else 0
        
        # Get at-risk students
        at_risk_query = "SELECT COUNT(*) as at_risk FROM student_records WHERE is_active = 0"
        at_risk_result = pd.read_sql_query(at_risk_query, conn)
        at_risk_students = at_risk_result.iloc[0]['at_risk'] if not at_risk_result.empty else 0
        
        # Get risk distribution
        risk_query = """
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
        risk_result = pd.read_sql_query(risk_query, conn)
        
        conn.close()
        
        return total_students, at_risk_students, risk_result
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return 0, 0, pd.DataFrame()

def main():
    """Main application"""
    st.title("🎓 AI-Powered Student Dropout Prediction System")
    
    # Initialize database
    create_database()
    
    # Check if database has data, if not generate sample data
    try:
        conn = sqlite3.connect('student_dropout.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM student_records")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            with st.spinner("Generating sample data..."):
                df = generate_sample_data(1000)
                conn = sqlite3.connect('student_dropout.db')
                df.to_sql('student_records', conn, if_exists='replace', index=False)
                conn.close()
                st.success("Sample data generated successfully!")
    except Exception as e:
        st.error(f"Error initializing data: {e}")
    
    # Sidebar navigation
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
    
    # Get real data from database
    total_students, at_risk_students, risk_data = get_database_stats()
    
    if total_students > 0:
        at_risk_percentage = (at_risk_students / total_students * 100)
        success_rate = ((total_students - at_risk_students) / total_students * 100)
    else:
        at_risk_percentage = 0
        success_rate = 0
    
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
    
    # Risk distribution
    st.subheader("📈 Risk Distribution")
    
    if not risk_data.empty:
        total = risk_data['count'].sum()
        risk_data['percentage'] = (risk_data['count'] / total * 100).round(1)
        
        # Create pie chart
        fig = px.pie(risk_data, values='count', names='risk_level', 
                     title='Student Risk Level Distribution',
                     color_discrete_map={'Green': '#2E8B57', 'Amber': '#FF8C00', 'Red': '#DC143C'})
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        # Display summary table
        st.subheader("Risk Level Summary")
        st.dataframe(risk_data, use_container_width=True)
    else:
        st.info("No data available for risk distribution")

def display_student_search():
    """Display student search interface"""
    st.subheader("🔍 Student Search & Prediction")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        student_id = st.text_input("Enter Student ID", "STU00001")
        
        if st.button("Search Student"):
            try:
                conn = sqlite3.connect('student_dropout.db')
                query = "SELECT * FROM student_records WHERE student_id = ?"
                result = pd.read_sql_query(query, conn, params=(student_id,))
                conn.close()
                
                if not result.empty:
                    student_data = result.iloc[0].to_dict()
                    
                    # Make prediction
                    risk_score, risk_level = simple_dropout_prediction(student_data)
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Risk Score", f"{risk_score:.2f}")
                    
                    with col_b:
                        st.metric("Risk Level", risk_level)
                    
                    with col_c:
                        st.metric("Probability", f"{risk_score:.1%}")
                    
                    # Risk gauge
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = risk_score * 100,
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
                        st.error(f"🔴 HIGH RISK - {risk_score:.1%} probability of dropout")
                    elif risk_level == "Amber":
                        st.warning(f"🟡 MEDIUM RISK - {risk_score:.1%} probability of dropout")
                    else:
                        st.success(f"🟢 LOW RISK - {risk_score:.1%} probability of dropout")
                else:
                    st.warning(f"Student {student_id} not found in database")
                    
            except Exception as e:
                st.error(f"Error searching for student: {e}")
    
    with col2:
        st.subheader("Student Information")
        if st.button("Show Sample Student"):
            # Show sample student data
            sample_data = {
                'student_id': 'STU00001',
                'name': 'John Doe',
                'age': 18,
                'gender': 'M',
                'socioeconomic_status': 'Middle',
                'attendance_rate': 0.65,
                'avg_test_score': 48.7,
                'fee_default_rate': 0.9
            }
            
            for key, value in sample_data.items():
                st.write(f"**{key}:** {value}")

def display_data_management():
    """Display data management interface"""
    st.subheader("📊 Data Management")
    
    if st.button("Generate New Sample Data"):
        with st.spinner("Generating sample data..."):
            df = generate_sample_data(1000)
            
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
