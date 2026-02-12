"""Modul untuk form input data inspector"""
import streamlit as st
from utils.lookup_tables import PRODUCT_PROPERTIES, FAULT_MAPPING


def render_specification_form():
    """Render form input spesifikasi pompa"""
    st.subheader("📋 Spesifikasi Pompa (Context Data)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        product_type = st.selectbox(
            "Product Type",
            options=list(PRODUCT_PROPERTIES.keys()),
            index=1,
            help="Jenis produk yang dipompa"
        )
    
    with col2:
        foundation_type = st.radio(
            "Foundation Type",
            options=["Rigid", "Flexible"],
            index=0,
            help="Rigid = concrete slab, Flexible = steel skid"
        )
    
    with col3:
        pump_size = st.selectbox(
            "Pump Size Class",
            options=["Small", "Medium", "Large"],
            index=1,
            help="Small: <50 m³/h, Medium: 50-200 m³/h, Large: >200 m³/h"
        )
    
    col4, col5 = st.columns(2)
    
    with col4:
        installation_year = st.number_input(
            "Installation Year",
            min_value=1990,
            max_value=2026,
            value=2018,
            help="Tahun instalasi pompa"
        )
    
    with col5:
        rated_rpm = st.number_input(
            "Rated Speed (RPM)",
            min_value=0,
            max_value=5000,
            value=2950,
            help="Kecepatan rated motor/pompa"
        )
    
    return {
        "product_type": product_type,
        "foundation_type": foundation_type,
        "pump_size": pump_size,
        "installation_year": int(installation_year),
        "rated_rpm": int(rated_rpm)
    }


def render_vibration_input(section_name, key_prefix):
    """Render form input vibrasi untuk Driver atau Driven"""
    st.subheader(f"📊 Vibrasi - {section_name}")
    
    directions = ["H", "V", "A"]
    cols = st.columns(3)
    
    vibration_data = {}
    
    for idx, direction in enumerate(directions):
        with cols[idx]:
            st.markdown(f"**{direction} ({FAULT_MAPPING[direction]})**")
            
            col_de, col_nde = st.columns(2)
            
            with col_de:
                de_value = st.number_input(
                    f"DE ({direction})",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.1,
                    key=f"{key_prefix}_de_{direction}",
                    help="Drive End vibration (mm/s RMS)"
                )
            
            with col_nde:
                nde_value = st.number_input(
                    f"NDE ({direction})",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.1,
                    key=f"{key_prefix}_nde_{direction}",
                    help="Non-Drive End vibration (mm/s RMS)"
                )
            
            vibration_data[f"DE_{direction}"] = de_value
            vibration_data[f"NDE_{direction}"] = nde_value
    
    with st.expander("🔍 Advanced Vibration Data (Optional)"):
        col1, col2 = st.columns(2)
        
        with col1:
            hf_5_16khz = st.number_input(
                "HF Band 5-16 kHz (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key=f"{key_prefix}_hf",
                help="High frequency vibration for cavitation/bearing detection"
            )
        
        with col2:
            demod_g = st.number_input(
                "Demodulation (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key=f"{key_prefix}_demod",
                help="Demodulated signal for early bearing defect"
            )
        
        vibration_data["HF_5_16kHz"] = hf_5_16khz
        vibration_data["Demodulation"] = demod_g
    
    return vibration_data


def render_operational_input():
    """Render form input operasional (pressure, flow, dll)"""
    st.subheader("⚙️ Data Operasional")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        suction_pressure = st.number_input(
            "Suction Pressure (kPa)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=1.0,
            help="Tekanan suction di nozzle pompa"
        )
    
    with col2:
        discharge_pressure = st.number_input(
            "Discharge Pressure (kPa)",
            min_value=0.0,
            max_value=2000.0,
            value=400.0,
            step=1.0,
            help="Tekanan discharge di nozzle pompa"
        )
    
    with col3:
        flow_rate = st.number_input(
            "Flow Rate (m³/h)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=1.0,
            help="Laju alir produk"
        )
    
    return {
        "suction_pressure": suction_pressure,
        "discharge_pressure": discharge_pressure,
        "flow_rate": flow_rate
    }


def render_rpm_input():
    """Render input RPM aktual"""
    st.subheader("🔄 Actual RPM")
    
    rpm = st.number_input(
        "Actual RPM (measured)",
        min_value=0,
        max_value=5000,
        value=2920,
        step=10,
        help="RPM aktual dari tachometer atau ADASH"
    )
    
    return float(rpm)


def render_electrical_input():
    """Render form input listrik (V & A)"""
    st.subheader("⚡ Data Listrik")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Voltage (V)**")
        v1 = st.number_input("L1", min_value=0, max_value=500, value=380, key="v1")
        v2 = st.number_input("L2", min_value=0, max_value=500, value=380, key="v2")
        v3 = st.number_input("L3", min_value=0, max_value=500, value=380, key="v3")
    
    with col2:
        st.markdown("**Current (A)**")
        i1 = st.number_input("L1", min_value=0.0, max_value=200.0, value=28.0, key="i1")
        i2 = st.number_input("L2", min_value=0.0, max_value=200.0, value=28.0, key="i2")
        i3 = st.number_input("L3", min_value=0.0, max_value=200.0, value=28.0, key="i3")
    
    with col3:
        st.markdown("**Status**")
        st.info("Input tegangan & arus per phase")
        st.warning("⚠️ Selisih >2% voltage atau >5% current = imbalance")
    
    return {
        "voltage_l1": float(v1),
        "voltage_l2": float(v2),
        "voltage_l3": float(v3),
        "current_l1": float(i1),
        "current_l2": float(i2),
        "current_l3": float(i3)
    }


def render_thermal_input():
    """Render form input thermal (optional)"""
    st.subheader("🌡️ Data Thermal (Optional)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temp_de = st.number_input(
            "Bearing Temp DE (°C)",
            min_value=0,
            max_value=150,
            value=65,
            help="Suhu bearing Drive End"
        )
    
    with col2:
        temp_nde = st.number_input(
            "Bearing Temp NDE (°C)",
            min_value=0,
            max_value=150,
            value=65,
            help="Suhu bearing Non-Drive End"
        )
    
    return {
        "temp_de": float(temp_de),
        "temp_nde": float(temp_nde)
    }


def collect_all_inputs():
    """Kumpulkan semua input dari form"""
    
    with st.sidebar:
        st.header("🔧 Metadata")
        pump_tag = st.text_input("Pump Tag", value="PT-XXX-001")
        inspector_name = st.text_input("Inspector Name")
        inspection_date = st.date_input("Inspection Date")
        location = st.text_input("Location/Terminal", value="Integrated Terminal")
    
    st.title("Pump Diagnosis Tool")
    st.markdown("---")
    
    spec_data = render_specification_form()
    st.markdown("---")
    
    vibration_driver = render_vibration_input("Driver (Motor)", "driver")
    st.markdown("---")
    
    vibration_driven = render_vibration_input("Driven (Pump)", "driven")
    st.markdown("---")
    
    operational_data = render_operational_input()
    st.markdown("---")
    
    rpm_actual = render_rpm_input()
    st.markdown("---")
    
    electrical_data = render_electrical_input()
    st.markdown("---")
    
    thermal_data = render_thermal_input()
    
    st.markdown("---")
    col_submit, col_clear = st.columns(2)
    
    with col_submit:
        submit_button = st.button("🔍 Run Diagnosis", type="primary", use_container_width=True)
    
    with col_clear:
        clear_button = st.button("🗑️ Clear Form", use_container_width=True)
    
    return {
        "metadata": {
            "pump_tag": pump_tag,
            "inspector_name": inspector_name,
            "inspection_date": inspection_date,
            "location": location
        },
        "specification": spec_data,
        "vibration": {
            "driver": vibration_driver,
            "driven": vibration_driven
        },
        "operational": operational_data,
        "rpm": rpm_actual,
        "electrical": electrical_data,
        "thermal": thermal_data,
        "submit_clicked": submit_button,
        "clear_clicked": clear_button
    }
