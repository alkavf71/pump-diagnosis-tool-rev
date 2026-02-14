"""Main entry point for Pump Diagnosis Tool - 100% compliant with API/ISO/IEC"""
import streamlit as st
from datetime import datetime

# Import modules (pastikan struktur folder benar)
from modules.data_input import collect_all_inputs
from modules.diagnosis_engine import run_complete_diagnosis
from modules.report_generator import (
    display_diagnosis_summary,
    display_detailed_analysis,
    display_action_plan,
    generate_excel_report
)

# Set page config
st.set_page_config(
    page_title="Pump Diagnosis Tool - Pertamina Patra Niaga",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit application"""
    # Sidebar header
    st.sidebar.image("https://pertamina.com/logo.png", width=150)  # Optional: ganti dengan logo Pertamina
    st.sidebar.markdown("## 🔧 Pump Diagnosis Tool")
    st.sidebar.markdown("**PT Pertamina Patra Niaga**")
    st.sidebar.markdown("Asset Integrity Management")
    st.sidebar.markdown("---")
    
    # Collect inputs
    input_data = collect_all_inputs()
    
    # Process diagnosis if submit clicked
    if input_data["submit_clicked"]:
        with st.spinner("🔄 Running diagnosis..."):
            try:
                # Run complete diagnosis with causal hierarchy
                diagnosis_result = run_complete_diagnosis(input_data)
                
                # Display results
                display_diagnosis_summary(diagnosis_result)
                st.markdown("---")
                display_detailed_analysis(diagnosis_result)
                st.markdown("---")
                display_action_plan(
                    diagnosis_result["action_plan"], 
                    diagnosis_result=diagnosis_result
                )
                st.markdown("---")
                
                # Excel export
                st.subheader("📥 Export Diagnosis Report")
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("📄 Generate Excel Report", type="primary"):
                        excel_df = generate_excel_report(diagnosis_result)
                        
                        # Save to /tmp (required for Streamlit Cloud)
                        excel_file = f"/tmp/pump_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        excel_df.to_excel(excel_file, index=False)
                        
                        # Provide download link
                        with open(excel_file, "rb") as f:
                            st.download_button(
                                label="⬇️ Download Excel Report",
                                data=f,
                                file_name=f"pump_diagnosis_{input_data['metadata']['pump_tag']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                
                with col2:
                    st.caption("""
                    ℹ️ **Report Includes**: 
                    • Full diagnosis with causal hierarchy 
                    • Compliance statement (API 610, ISO 13373, IEC 60034) 
                    • Action plan with timeline & PIC 
                    • Raw data for audit trail
                    """)
            
            except Exception as e:
                st.error(f"❌ Diagnosis error: {str(e)}")
                st.exception(e)
    
    # Clear form if clicked
    if input_data["clear_clicked"]:
        st.experimental_rerun()
    
    # Footer
    st.markdown("---")
    st.caption("""
    **Compliance Statement**: This tool implements causal hierarchy per API 610 12th Ed. Annex L.3.2, 
    vibration severity per ISO 10816-3:2022, fault identification per ISO 13373-3:2020, 
    electrical monitoring per IEC 60034-1:2017 §4.2, and bearing defect detection per ISO 15243:2017 §5.2. 
    All calculations are traceable to clause-specific standards for audit readiness.
    """)

if __name__ == "__main__":
    main()
