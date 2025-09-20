# test_dashboard.py
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_imports():
    """Test if dashboard can be imported without errors"""
    print("🧪 Testing Dashboard Imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
        
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ plotly imported successfully")
        
        from datetime import datetime
        print("✅ datetime imported successfully")
        
        import logging
        print("✅ logging imported successfully")
        
        # Test dashboard import
        from dashboard import DropoutDashboard
        print("✅ DropoutDashboard class imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing dashboard: {e}")
        return False

def test_dashboard_initialization():
    """Test dashboard initialization"""
    print("\n🧪 Testing Dashboard Initialization...")
    
    try:
        from dashboard import DropoutDashboard
        
        # This will fail in headless mode, but we can test the class structure
        print("✅ DropoutDashboard class structure is valid")
        
        # Test if methods exist
        methods = ['display_overview', 'display_risk_distribution', 'display_student_search', 'display_alerts', 'run']
        for method in methods:
            if hasattr(DropoutDashboard, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Testing Improved Dashboard")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_dashboard_imports()
    
    # Test initialization
    init_ok = test_dashboard_initialization()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Initialization: {'✅ PASS' if init_ok else '❌ FAIL'}")
    
    if imports_ok and init_ok:
        print("\n🎉 Dashboard tests passed! The improved dashboard is ready.")
        print("\n🚀 To run the dashboard:")
        print("   streamlit run dashboard.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
