"""Modul untuk generate laporan (PDF/Excel/display)"""
import streamlit as st
import pandas as pd


def display_diagnosis_summary(diagnosis_result):
    """Display summary diagnosis di Streamlit"""
    summary = diagnosis_result["summary"]
    
    st.markdown(f"### 📊 Executive Summary")
    
    color_map = {
        "green": "#d4edda",
        "yellow": "#fff3cd",
        "orange": "#ffe0b2",
        "red": "#f8d7da"
    }
    
    bg_color = color_map.get(summary["color"], "#ffffff")
    
    st.markdown(
        f"""
        <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; border-left: 5px solid {summary['color']};">
            <h3>{summary['summary_text']}</h3>
            <p><strong>Risk Level:</strong> {summary['risk_level']} (Score: {summary['risk_score']}/100)</p>
            <p><strong>Recommended Actions:</strong> {summary['action_count']} items</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_detailed_analysis(diagnosis_result):
    """Display detailed analysis per component"""
    analyses = diagnosis_result["analyses"]
    
    st.markdown("### 🔍 Detailed Analysis")
    
    # Tambahkan tab FFT ke daftar tabs
    tabs = st.tabs(["Hydraulic", "Electrical", "Mechanical", "Thermal", "FFT Spectrum"])
    
    # Tab 1: Hydraulic
    with tabs[0]:
        hydraulic = analyses["hydraulic"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "NPSHa",
                f"{hydraulic['npsha']:.2f} m",
                delta=f"{hydraulic['npsha_margin']:.2f} m margin",
                delta_color="normal" if hydraulic['npsha_margin'] > 0 else "inverse"
            )
        
        with col2:
            status_color = "red" if hydraulic['cavitation_risk'] == "HIGH" else "green"
            st.markdown(f"**Cavitation Risk:** <span style='color:{status_color}'>{hydraulic['cavitation_risk']}</span>", unsafe_allow_html=True)
            st.markdown(f"*{hydraulic['cavitation_status']}*")
        
        with col3:
            st.metric(
                "Flow Ratio",
                f"{hydraulic['flow_ratio']:.2f}× BEP",
                delta=None
            )
            st.markdown(f"*{hydraulic['flow_recommendation']}*")
        
        if hydraulic.get("has_issue"):
            st.warning("⚠️ **Hydraulic Issue Detected**")
            st.info(hydraulic['cavitation_status'])
            if hydraulic['flow_status'] != "NORMAL":
                st.info(hydraulic['flow_recommendation'])
    
    # Tab 2: Electrical
    with tabs[1]:
        electrical = analyses["electrical"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Voltage Imbalance",
                f"{electrical['voltage']['imbalance_pct']:.1f}%",
                delta=None
            )
            st.markdown(f"*Status: {electrical['voltage']['status']}*")
        
        with col2:
            st.metric(
                "Current Imbalance",
                f"{electrical['current']['imbalance_pct']:.1f}%",
                delta=None
            )
            st.markdown(f"*Status: {electrical['current']['status']}*")
        
        with col3:
            st.metric(
                "Motor Load",
                f"{electrical['load']['percentage']:.1f}%",
                delta=f"{electrical['load']['percentage'] - 100:.1f}% from FLA"
            )
            st.markdown(f"*Status: {electrical['load']['status']}*")
        
        if electrical.get("has_issue"):
            st.warning("⚠️ **Electrical Issue Detected**")
            for rec in electrical['recommendations']:
                st.info(rec)
    
    # Tab 3: Mechanical
    with tabs[2]:
        mechanical = analyses["mechanical"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Driver Max Vib",
                f"{mechanical['driver']['averages']['Overall_Max']:.2f} mm/s",
                delta=None
            )
            st.markdown(f"*Zone {mechanical['driver']['overall_zone']}*")
        
        with col2:
            st.metric(
                "Driven Max Vib",
                f"{mechanical['driven']['averages']['Overall_Max']:.2f} mm/s",
                delta=None
            )
            st.markdown(f"*Zone {mechanical['driven']['overall_zone']}*")
        
        with col3:
            st.metric(
                "Primary Component",
                mechanical['primary_component']
            )
            st.markdown(f"*Primary Fault: {mechanical['primary_fault']}*")
        
        if mechanical.get("has_issue"):
            st.warning("⚠️ **Mechanical Issue Detected**")
            for rec in mechanical['recommendations']:
                st.info(rec)
    
    # Tab 4: Thermal
    with tabs[3]:
        thermal = analyses["thermal"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Bearing DE Temp",
                f"{thermal['de']['temperature']:.1f}°C",
                delta=f"{thermal['de']['rise_above_ambient']:.1f}°C above ambient"
            )
            st.markdown(f"*Status: {thermal['de']['status']}*")
        
        with col2:
            st.metric(
                "Bearing NDE Temp",
                f"{thermal['nde']['temperature']:.1f}°C",
                delta=f"{thermal['nde']['rise_above_ambient']:.1f}°C above ambient"
            )
            st.markdown(f"*Status: {thermal['nde']['status']}*")
        
        with col3:
            st.metric(
                "Temp Difference",
                f"{thermal['delta_temp']:.1f}°C",
                delta=None
            )
        
        if thermal.get("has_issue"):
            st.warning("⚠️ **Thermal Issue Detected**")
            for rec in thermal['recommendations']:
                st.info(rec)
    
    # Tab 5: FFT Spectrum (BARU)
    with tabs[4]:
        fft_analysis = analyses.get("fft", {})
        
        if not fft_analysis.get("available", False):
            st.info("ℹ️ FFT spectrum data not available or not entered")
            st.caption("To enable FFT analysis, input peak frequency data in the FFT Spectrum section of the form.")
            return
        
        st.markdown(f"**RPM Actual:** {fft_analysis['rpm_actual']} RPM ({fft_analysis['rpm_hz']} Hz)")
        st.markdown(f"**Peak Findings:** {fft_analysis['count']} significant peaks detected")
        
        if fft_analysis["count"] > 0:
            # Group findings by confidence level
            high_confidence = [f for f in fft_analysis["findings"] if f["confidence"] == "HIGH"]
            medium_confidence = [f for f in fft_analysis["findings"] if f["confidence"] == "MEDIUM"]
            low_confidence = [f for f in fft_analysis["findings"] if f["confidence"] == "LOW"]
            
            # Display HIGH confidence first
            if high_confidence:
                st.error("🔴 **HIGH CONFIDENCE FINDINGS** (Requires immediate attention)")
                for idx, finding in enumerate(high_confidence, 1):
                    with st.expander(f"⚠️ Peak #{idx}: {finding['component']} - {finding['direction']}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Frequency", f"{finding['frequency_hz']} Hz")
                            st.metric("Ratio to RPM", f"{finding['ratio_to_rpm']}x")
                        
                        with col2:
                            st.metric("Amplitude", f"{finding['amplitude_mms']} mm/s")
                            st.metric("Confidence", finding["confidence"])
                        
                        with col3:
                            st.markdown(f"**Fault:** {finding['fault']}")
                            st.error("⚠️ HIGH CONFIDENCE - Requires attention")
            
            # Display MEDIUM confidence
            if medium_confidence:
                st.warning("🟠 **MEDIUM CONFIDENCE FINDINGS** (Monitor closely)")
                for idx, finding in enumerate(medium_confidence, len(high_confidence) + 1):
                    with st.expander(f"⚠️ Peak #{idx}: {finding['component']} - {finding['direction']}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Frequency", f"{finding['frequency_hz']} Hz")
                            st.metric("Ratio to RPM", f"{finding['ratio_to_rpm']}x")
                        
                        with col2:
                            st.metric("Amplitude", f"{finding['amplitude_mms']} mm/s")
                            st.metric("Confidence", finding["confidence"])
                        
                        with col3:
                            st.markdown(f"**Fault:** {finding['fault']}")
                            st.warning("⚠️ MEDIUM CONFIDENCE - Monitor closely")
            
            # Display LOW confidence (collapsed by default)
            if low_confidence:
                with st.expander(f"⚪ LOW CONFIDENCE FINDINGS ({len(low_confidence)} peaks)", expanded=False):
                    for idx, finding in enumerate(low_confidence, len(high_confidence) + len(medium_confidence) + 1):
                        st.markdown(f"**Peak #{idx}:** {finding['frequency_hz']} Hz ({finding['ratio_to_rpm']}x RPM) - {finding['fault']}")
        else:
            st.success("✅ No significant peaks detected in FFT spectrum")


def display_action_plan(action_plan):
    """Display action plan dengan timeline"""
    st.markdown("### 📋 Recommended Action Plan")
    
    actions = action_plan["actions"]
    
    if not actions:
        st.success("✅ No immediate actions required. Continue routine monitoring.")
        return
    
    priority_order = ["CRITICAL", "IMMEDIATE", "HIGH", "MEDIUM", "LOW", "ROUTINE"]
    
    for priority in priority_order:
        priority_actions = [a for a in actions if a.get("priority") == priority]
        
        if priority_actions:
            priority_color = {
                "CRITICAL": "red",
                "IMMEDIATE": "orange",
                "HIGH": "orange",
                "MEDIUM": "yellow",
                "LOW": "blue",
                "ROUTINE": "green"
            }.get(priority, "gray")
            
            st.markdown(f"#### <span style='color:{priority_color}'>{priority}</span>", unsafe_allow_html=True)
            
            for idx, action in enumerate(priority_actions, 1):
                with st.expander(f"**{idx}. {action['action']}**"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Timeline:** {action['timeline']}")
                    
                    with col2:
                        st.markdown(f"**PIC:** {action['pic']}")
                    
                    with col3:
                        if "standard" in action:
                            st.markdown(f"**Standard:** {action['standard']}")


def generate_excel_report(diagnosis_result):
    """Generate Excel report untuk download"""
    
    data = {
        "Category": [],
        "Parameter": [],
        "Value": [],
        "Status": [],
        "Recommendation": []
    }
    
    analyses = diagnosis_result["analyses"]
    action_plan = diagnosis_result["action_plan"]
    
    # Hydraulic
    hydraulic = analyses["hydraulic"]
    data["Category"].extend(["Hydraulic", "Hydraulic", "Hydraulic"])
    data["Parameter"].extend(["NPSHa", "Flow Ratio", "Cavitation Risk"])
    data["Value"].extend([
        f"{hydraulic['npsha']:.2f} m",
        f"{hydraulic['flow_ratio']:.2f}× BEP",
        hydraulic['cavitation_risk']
    ])
    data["Status"].extend([
        "OK" if hydraulic['npsha_margin'] > 0 else "ISSUE",
        "OK" if hydraulic['flow_status'] == "NORMAL" else "ISSUE",
        "OK" if hydraulic['cavitation_risk'] == "LOW" else "ISSUE"
    ])
    data["Recommendation"].extend([
        hydraulic['cavitation_status'],
        hydraulic['flow_recommendation'],
        ""
    ])
    
    # Electrical
    electrical = analyses["electrical"]
    data["Category"].extend(["Electrical", "Electrical", "Electrical"])
    data["Parameter"].extend(["Voltage Imbalance", "Current Imbalance", "Motor Load"])
    data["Value"].extend([
        f"{electrical['voltage']['imbalance_pct']:.1f}%",
        f"{electrical['current']['imbalance_pct']:.1f}%",
        f"{electrical['load']['percentage']:.1f}%"
    ])
    data["Status"].extend([
        electrical['voltage']['status'],
        electrical['current']['status'],
        electrical['load']['status']
    ])
    data["Recommendation"].extend(electrical['recommendations'][:3] if len(electrical['recommendations']) >= 3 else electrical['recommendations'] + [""] * (3 - len(electrical['recommendations'])))
    
    # Mechanical
    mechanical = analyses["mechanical"]
    data["Category"].extend(["Mechanical", "Mechanical"])
    data["Parameter"].extend(["Driver Vibration", "Driven Vibration"])
    data["Value"].extend([
        f"{mechanical['driver']['averages']['Overall_Max']:.2f} mm/s (Zone {mechanical['driver']['overall_zone']})",
        f"{mechanical['driven']['averages']['Overall_Max']:.2f} mm/s (Zone {mechanical['driven']['overall_zone']})"
    ])
    data["Status"].extend([
        "OK" if mechanical['driver']['overall_zone'] in ["A", "B"] else "ISSUE",
        "OK" if mechanical['driven']['overall_zone'] in ["A", "B"] else "ISSUE"
    ])
    data["Recommendation"].extend(mechanical['recommendations'][:2] if len(mechanical['recommendations']) >= 2 else mechanical['recommendations'] + [""] * (2 - len(mechanical['recommendations'])))
    
    # Thermal
    thermal = analyses["thermal"]
    data["Category"].extend(["Thermal", "Thermal"])
    data["Parameter"].extend(["Bearing DE Temp", "Bearing NDE Temp"])
    data["Value"].extend([
        f"{thermal['de']['temperature']:.1f}°C",
        f"{thermal['nde']['temperature']:.1f}°C"
    ])
    data["Status"].extend([
        thermal['de']['status'],
        thermal['nde']['status']
    ])
    data["Recommendation"].extend(thermal['recommendations'][:2] if len(thermal['recommendations']) >= 2 else thermal['recommendations'] + [""] * (2 - len(thermal['recommendations'])))
    
    # FFT Analysis (BARU)
    fft_analysis = analyses.get("fft", {})
    if fft_analysis.get("available", False) and fft_analysis.get("count", 0) > 0:
        data["Category"].append("FFT Spectrum")
        data["Parameter"].append("Significant Peaks")
        data["Value"].append(f"{fft_analysis['count']} peaks detected")
        data["Status"].append("ANALYSIS_COMPLETE")
        data["Recommendation"].append(f"RPM: {fft_analysis['rpm_actual']} RPM")
        
        # Add individual peak findings
        for finding in fft_analysis["findings"]:
            data["Category"].append("FFT Peak")
            data["Parameter"].append(f"{finding['component']} {finding['direction']}")
            data["Value"].append(f"{finding['frequency_hz']} Hz ({finding['ratio_to_rpm']}x RPM)")
            data["Status"].append(finding["confidence"])
            data["Recommendation"].append(finding["fault"])
    
    # Action Plan
    for action in action_plan["actions"]:
        data["Category"].append("Action Plan")
        data["Parameter"].append(action.get("priority", ""))
        data["Value"].append(action.get("action", ""))
        data["Status"].append(action.get("timeline", ""))
        data["Recommendation"].append(action.get("pic", ""))
    
    df = pd.DataFrame(data)
    return df
