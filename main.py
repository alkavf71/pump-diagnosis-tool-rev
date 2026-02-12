"""
Pump Diagnosis Tool - PT Pertamina Patra Niaga
Streamlit Application - Causal Hierarchy Diagnosis
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# Import modules
from modules.data_input import collect_all_inputs
from modules.diagnosis_engine import run_complete_diagnosis
from modules.report_generator import (
    display_diagnosis_summary,
    display_detailed_analysis,
    display_action_plan,
    generate_excel_report
)

# Page configuration
st.set_page_config(
    page_title="Pump Diagnosis Tool - Pertamina Patra Niaga",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<p class="main-header">⚙️ Pump Diagnosis Tool</p>', unsafe_allow_html=True)
    st.markdown("**PT Pertamina Patra Niaga - Integrated Terminal**")
    st.markdown("---")
    
    # Collect inputs
    input_data = collect_all_inputs()
    
    # Handle clear button
    if input_data["clear_clicked"]:
        st.rerun()
    
    # Run diagnosis when submit clicked
    if input_data["submit_clicked"]:
        with st.spinner("🔍 Running diagnosis..."):
            diagnosis_result = run_complete_diagnosis(input_data)
        
        st.success("✅ Diagnosis complete!")
        st.markdown("---")
        
        # Display results in tabs
        result_tabs = st.tabs([
            "📋 Summary",
            "🔍 Detailed Analysis",
            "📋 Action Plan",
            "📊 Export Report"
        ])
        
        # Tab 1: Summary
        with result_tabs[0]:
            display_diagnosis_summary(diagnosis_result)
            
            col1, col2, col3, col4 = st.columns(4)
            
            analyses = diagnosis_result["analyses"]
            
            with col1:
                hydraulic_status = "⚠️ ISSUE" if analyses["hydraulic"].get("has_issue") else "✅ OK"
                st.metric("Hydraulic", hydraulic_status)
            
            with col2:
                electrical_status = "⚠️ ISSUE" if analyses["electrical"].get("has_issue") else "✅ OK"
                st.metric("Electrical", electrical_status)
            
            with col3:
                mechanical_status = "⚠️ ISSUE" if analyses["mechanical"].get("has_issue") else "✅ OK"
                st.metric("Mechanical", mechanical_status)
            
            with col4:
                thermal_status = "⚠️ ISSUE" if analyses["thermal"].get("has_issue") else "✅ OK"
                st.metric("Thermal", thermal_status)
        
        # Tab 2: Detailed Analysis
        with result_tabs[1]:
            display_detailed_analysis(diagnosis_result)
        
        # Tab 3: Action Plan
        with result_tabs[2]:
            display_action_plan(diagnosis_result["action_plan"])
        
        # Tab 4: Export Report
        with result_tabs[3]:
            st.markdown("### 📊 Export Diagnosis Report")
            
            excel_df = generate_excel_report(diagnosis_result)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Preview Report")
                st.dataframe(excel_df, use_container_width=True)
            
            with col2:
                st.markdown("#### Download Options")
                
                excel_file = f"/tmp/pump_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                csv_file = f"/tmp/pump_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                excel_df.to_csv(csv_file, index=False)

                with open(csv_file, 'rb') as f:
                    st.download_button(
                        label="📥 Download CSV Report",
                        data=f,
                        file_name=f"pump_diagnosis_{diagnosis_result['metadata']['pump_tag']}.csv",
                        mime="text/csv"
                    )
                
                st.info("📄 PDF report generation will be added in future update!")
        
        # Compliance statement
        st.markdown("---")
        st.markdown("**Standards Compliance:**")
        st.caption("""
        This diagnosis complies with:
        - ISO 10816-3:2022 (Mechanical Vibration)
        - API 610 12th Ed. (Centrifugal Pumps)
        - ISO 13373-3:2020 (Condition Monitoring)
        - IEC 60034-1 (Rotating Electrical Machines)
        - Pertamina SOP Asset Integrity
        """)

if __name__ == "__main__":
    main()
