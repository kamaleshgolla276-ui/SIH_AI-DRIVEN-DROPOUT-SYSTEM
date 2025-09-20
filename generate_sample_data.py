# generate_sample_data.py
import pandas as pd
import numpy as np
from database_connector import DatabaseConnector
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_data(n_students=1000):
    """Generate sample student data"""
    logger.info(f"Generating {n_students} sample student records...")
    
    # Generate student IDs
    student_ids = [f'STU{i:05d}' for i in range(1, n_students+1)]
    
    # Generate synthetic data
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
    
    # Create DataFrame
    students_df = pd.DataFrame(data)
    
    # Create target variable with meaningful correlations
    students_df['is_active'] = 1  # Default to active
    
    # Create dropout patterns based on features
    dropout_conditions = (
        (students_df['attendance_rate'] < 0.7) |
        (students_df['avg_test_score'] < 50) |
        (students_df['fee_default_rate'] > 0.8) |
        (students_df['socioeconomic_status'] == 'Low') |
        (students_df['distance_from_school_km'] > 10)
    )
    
    students_df.loc[dropout_conditions, 'is_active'] = 0
    
    # Add some noise
    mask = np.random.random(n_students) < 0.05
    students_df.loc[mask, 'is_active'] = 1 - students_df.loc[mask, 'is_active']
    
    logger.info(f"Generated {len(students_df)} student records")
    logger.info(f"Active students: {students_df['is_active'].sum()}")
    logger.info(f"Dropout students: {len(students_df) - students_df['is_active'].sum()}")
    logger.info(f"Dropout rate: {(1 - students_df['is_active'].mean())*100:.2f}%")
    
    return students_df

def populate_database():
    """Populate database with sample data"""
    try:
        # Initialize database connector
        db_connector = DatabaseConnector()
        
        # Generate sample data
        students_df = generate_sample_data(1000)
        
        # Insert data into database
        logger.info("Inserting data into database...")
        success_count = 0
        
        for _, row in students_df.iterrows():
            if db_connector.insert_student_record(row.to_dict()):
                success_count += 1
        
        logger.info(f"Successfully inserted {success_count}/{len(students_df)} records")
        
        # Close database connection
        db_connector.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error populating database: {e}")
        return False

if __name__ == "__main__":
    print("🎓 Generating Sample Data for Student Dropout Prediction System")
    print("=" * 60)
    
    if populate_database():
        print("✅ Sample data generated and inserted successfully!")
        print("You can now run the application with: python run_app.py")
    else:
        print("❌ Error generating sample data")
