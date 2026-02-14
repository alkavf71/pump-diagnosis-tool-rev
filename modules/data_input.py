"""Form input data inspector - 64 field sesuai standar"""
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
            help="Jenis produk yang dipompa (API 682 §5.4.2: stricter thresholds for volatile hydrocarbons)"
        )
    
    with col2:
        foundation_type = st.radio(
            "Foundation Type",
            options=["Rigid", "Flexible"],
            index=0,
            help="Rigid = concrete slab, Flexible = steel skid (ISO 10816-3 limits differ)"
        ).lower()
    
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
            help="Tahun instalasi pompa (ISO 55001 §8.2: age-based risk adjustment)"
        )
    
    with col5:
        rated_rpm = st.number_input(
            "Rated Speed (RPM)",
            min_value=0,
            max_value=5000,
            value=2950,
            help="Kecepatan rated motor/pompa (IEC 60034-1 §4.2: slip calculation)"
        )
    
    return {
        "product_type": product_type,
        "foundation_type": foundation_type,
        "pump_size": pump_size,
        "installation_year": int(installation_year),
        "rated_rpm": int(rated_rpm)
    }


def render_vibration_input_motor():
    """Render form input vibrasi untuk Motor (Driver)"""
    st.subheader("📊 Vibrasi - Motor (Driver)")
    
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
                    key=f"motor_de_{direction}",
                    help="Drive End vibration (mm/s RMS) - ISO 10816-3"
                )
            
            with col_nde:
                nde_value = st.number_input(
                    f"NDE ({direction})",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.1,
                    key=f"motor_nde_{direction}",
                    help="Non-Drive End vibration (mm/s RMS) - ISO 10816-3"
                )
            
            vibration_data[f"DE_{direction}"] = de_value
            vibration_data[f"NDE_{direction}"] = nde_value
    
    with st.expander("🔍 Advanced Vibration Data (Optional) - API 610 §6.3.3 & ISO 15243 §5.2"):
        col1, col2 = st.columns(2)
        
        with col1:
            hf_de = st.number_input(
                "HF Band 5-16 kHz DE (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key="motor_hf_de",
                help="High frequency vibration for cavitation detection (API 610 §6.3.3)"
            )
            hf_nde = st.number_input(
                "HF Band 5-16 kHz NDE (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key="motor_hf_nde",
                help="High frequency vibration for cavitation detection (API 610 §6.3.3)"
            )
        
        with col2:
            demod_de = st.number_input(
                "Demodulation DE (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key="motor_demod_de",
                help="Demodulated signal for early bearing defect (ISO 15243 §5.2)"
            )
            demod_nde = st.number_input(
                "Demodulation NDE (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key="motor_demod_nde",
                help="Demodulated signal for early bearing defect (ISO 15243 §5.2)"
            )
        
        vibration_data["HF_DE"] = hf_de
        vibration_data["HF_NDE"] = hf_nde
        vibration_data["Demodulation_DE"] = demod_de
        vibration_data["Demodulation_NDE"] = demod_nde
    
    return vibration_data


def render_vibration_input_pump():
    """Render form input vibrasi untuk Pompa (Driven)"""
    st.subheader("📊 Vibrasi - Pompa (Driven)")
    
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
                    key=f"pump_de_{direction}",
                    help="Drive End vibration (mm/s RMS) - ISO 10816-3"
                )
            
            with col_nde:
                nde_value = st.number_input(
                    f"NDE ({direction})",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.1,
                    key=f"pump_nde_{direction}",
                    help="Non-Drive End vibration (mm/s RMS) - ISO 10816-3"
                )
            
            vibration_data[f"DE_{direction}"] = de_value
            vibration_data[f"NDE_{direction}"] = nde_value
    
    with st.expander("🔍 Advanced Vibration Data (Optional) - API 610 §6.3.3 & ISO 15243 §5.2"):
        col1, col2 = st.columns(2)
        
        with col1:
            hf_de = st.number_input(
                "HF Band 5-16 kHz DE (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key="pump_hf_de",
                help="High frequency vibration for cavitation detection (API 610 §6.3.3)"
            )
            hf_nde = st.number_input(
                "HF Band 5-16 kHz NDE (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key="pump_hf_nde",
                help="High frequency vibration for cavitation detection (API 610 §6.3.3)"
            )
        
        with col2:
            demod_de = st.number_input(
                "Demodulation DE (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key="pump_demod_de",
                help="Demodulated signal for early bearing defect (ISO 15243 §5.2)"
            )
            demod_nde = st.number_input(
                "Demodulation NDE (g)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                key="pump_demod_nde",
                help="Demodulated signal for early bearing defect (ISO 15243 §5.2)"
            )
        
        vibration_data["HF_DE"] = hf_de
        vibration_data["HF_NDE"] = hf_nde
        vibration_data["Demodulation_DE"] = demod_de
        vibration_data["Demodulation_NDE"] = demod_nde
    
    return vibration_data


def render_fft_input_motor():
    """Render form input FFT spectrum untuk Motor"""
    st.subheader("📈 FFT Spectrum Analysis - Motor (Driver) (Optional)")
    st.caption("Input top 3 peak frequencies from ADASH FFT display (1-200 Hz)")
    
    col1, col2 = st.columns(2)
    
    fft_data = {}
    
    with col1:
        st.markdown("**📍 Drive End (DE) - Horizontal**")
        for i in range(1, 4):
            col_freq, col_amp = st.columns(2)
            with col_freq:
                freq = st.number_input(
                    f"Peak #{i} Frequency (Hz)",
                    min_value=0.0,
                    max_value=200.0,
                    value=0.0,
                    step=0.1,
                    key=f"motor_de_h_freq{i}"
                )
            with col_amp:
                amp = st.number_input(
                    f"Peak #{i} Amplitude (mm/s)",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.1,
                    key=f"motor_de_h_amp{i}"
                )
            fft_data[f"FFT_DE_H_Freq{i}"] = freq
            fft_data[f"FFT_DE_H_Amp{i}"] = amp
    
    with col2:
        st.markdown("**📍 Drive End (DE) - Axial**")
        for i in range(1, 4):
            col_freq, col_amp = st.columns(2)
            with col_freq:
                freq = st.number_input(
                    f"Peak #{i} Frequency (Hz)",
                    min_value=0.0,
                    max_value=200.0,
                    value=0.0,
                    step=0.1,
                    key=f"motor_de_a_freq{i}"
                )
            with col_amp:
                amp = st.number_input(
                    f"Peak #{i} Amplitude (mm/s)",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.1,
                    key=f"motor_de_a_amp{i}"
                )
            fft_data[f"FFT_DE_A_Freq{i}"] = freq
            fft_data[f"FFT_DE_A_Amp{i}"] = amp
    
    return fft_data


def render_fft_input_pump():
    """Render form input FFT spectrum untuk Pompa"""
    st.subheader("📈 FFT Spectrum Analysis - Pompa (Driven) (Optional)")
    st.caption("Input top 3 peak frequencies from ADASH FFT display (1-200 Hz)")
    
    col1, col2 = st.columns(2)
    
    fft_data = {}
    
    with col1:
        st.markdown("**📍 Drive End (DE) - Horizontal**")
        for i in range(1, 4):
            col_freq, col_amp = st.columns(2)
            with col_freq:
                freq = st.number_input(
                    f"Peak #{i} Frequency (Hz)",
                    min_value=0.0,
                    max_value=200.0,
                    value=0.0,
                    step=0.1,
                    key=f"pump_de_h_freq{i}"
                )
            with col_amp:
                amp = st.number_input(
                    f"Peak #{i} Amplitude (mm/s)",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.1,
                    key=f"pump_de_h_amp{i}"
                )
            fft_data[f"FFT_DE_H_Freq{i}"] = freq
            fft_data[f"FFT_DE_H_Amp{i}"] = amp
    
    with col2:
        st.markdown("**📍 Drive End (DE) - Axial**")
        for i in range(1, 4):
            col_freq, col_amp = st.columns(2)
            with col_freq:
                freq = st.number_input(
                    f"Peak #{i} Frequency (Hz)",
                    min_value=0.0,
                    max_value=200.0,
                    value=0.0,
                    step=0.1,
                    key=f"pump_de_a_freq{i}"
                )
            with col_amp:
                amp = st.number_input(
                    f"Peak #{i} Amplitude (mm/s)",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.1,
                    key=f"pump_de_a_amp{i}"
                )
            fft_data[f"FFT_DE_A_Freq{i}"] = freq
            fft_data[f"FFT_DE_A_Amp{i}"] = amp
    
    return fft_data


def render_operational_input():
    """Render form input operasional"""
    st.subheader("⚙️ Data Operasional")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        suction_pressure = st.number_input(
            "Suction Pressure (kPa)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=1.0,
            help="Tekanan suction di nozzle pompa (API 610 §6.3.3: NPSHa calculation)"
        )
    
    with col2:
        discharge_pressure = st.number_input(
            "Discharge Pressure (kPa)",
            min_value=0.0,
            max_value=2000.0,
            value=400.0,
            step=1.0,
            help="Tekanan discharge di nozzle pompa (ISO 13709 §7.2.1: head calculation)"
        )
    
    with col3:
        flow_rate = st.number_input(
            "Flow Rate (m³/h)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=1.0,
            help="Laju alir produk (API 610 Annex L: BEP verification)"
        )
    
    return {
        "suction_pressure": suction_pressure,
        "discharge_pressure": discharge_pressure,
        "flow_rate": flow_rate
    }


def render_rpm_input():
    """Render input RPM aktual"""
    st.subheader("🔄 Actual RPM (IEC 60034-1 §4.2: Slip Calculation)")
    
    rpm = st.number_input(
        "Actual RPM (measured)",
        min_value=0,
        max_value=5000,
        value=2920,
        step=10,
        help="RPM aktual dari tachometer atau ADASH (IEC 60034-1 §4.2: required for slip monitoring)"
    )
    
    return float(rpm)


def render_electrical_input():
    """Render form input listrik"""
    st.subheader("⚡ Data Listrik (IEC 60034-1 §4.2)")
    
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
        st.warning("⚠️ Selisih >2% voltage atau >5% current = imbalance (IEC 60034-1)")
    
    return {
        "voltage_l1": float(v1),
        "voltage_l2": float(v2),
        "voltage_l3": float(v3),
        "current_l1": float(i1),
        "current_l2": float(i2),
        "current_l3": float(i3)
    }


def render_thermal_input():
    """Render form input thermal"""
    st.subheader("🌡️ Data Thermal (API 610 §11.3)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        temp_motor_de = st.number_input(
            "Motor DE (°C)",
            min_value=0,
            max_value=150,
            value=65,
            help="Suhu bearing Drive End motor (API 610 §11.3: seizure warning >85°C)"
        )
    
    with col2:
        temp_motor_nde = st.number_input(
            "Motor NDE (°C)",
            min_value=0,
            max_value=150,
            value=63,
            help="Suhu bearing Non-Drive End motor (API 610 §11.3: seizure warning >85°C)"
        )
    
    with col3:
        temp_pump_de = st.number_input(
            "Pump DE (°C)",
            min_value=0,
            max_value=150,
            value=68,
            help="Suhu bearing Drive End pompa (API 610 §11.3: seizure warning >85°C)"
        )
    
    with col4:
        temp_pump_nde = st.number_input(
            "Pump NDE (°C)",
            min_value=0,
            max_value=150,
            value=72,
            help="Suhu bearing Non-Drive End pompa (API 610 §11.3: seizure warning >85°C)"
        )
    
    with col5:
        temp_ambient = st.number_input(
            "Ambient (°C)",
            min_value=0,
            max_value=50,
            value=30,
            help="Suhu lingkungan untuk perhitungan rise above ambient"
        )
    
    return {
        "temp_motor_de": float(temp_motor_de),
        "temp_motor_nde": float(temp_motor_nde),
        "temp_pump_de": float(temp_pump_de),
        "temp_pump_nde": float(temp_pump_nde),
        "temp_ambient": float(temp_ambient),
        "product_type": "Gasoline",  # Will be overwritten by spec_data
        "lubricant_type": "grease"
    }


def collect_all_inputs():
    """Kumpulkan semua input dari form"""
    
    with st.sidebar:
        st.header("🔧 Metadata")
        pump_tag = st.text_input("Pump Tag", value="PT-XXX-001")
        inspector_name = st.text_input("Inspector Name")
        inspection_date = st.date_input("Inspection Date")
        location = st.text_input("Location/Terminal", value="Integrated Terminal")
    
    st.title("Pump Diagnosis Tool - 100% Compliant with API/ISO/IEC Standards")
    st.markdown("**PT Pertamina Patra Niaga - Asset Integrity Management**")
    st.markdown("---")
    
    spec_data = render_specification_form()
    st.markdown("---")
    
    vibration_motor = render_vibration_input_motor()
    st.markdown("---")
    
    vibration_pump = render_vibration_input_pump()
    st.markdown("---")
    
    operational_data = render_operational_input()
    st.markdown("---")
    
    rpm_actual = render_rpm_input()
    st.markdown("---")
    
    electrical_data = render_electrical_input()
    st.markdown("---")
    
    thermal_data = render_thermal_input()
    thermal_data["product_type"] = spec_data["product_type"]  # Overwrite with actual product
    st.markdown("---")
    
    fft_motor = render_fft_input_motor()
    st.markdown("---")
    
    fft_pump = render_fft_input_pump()
    
    st.markdown("---")
    col_submit, col_clear = st.columns(2)
    
    with col_submit:
        submit_button = st.button("🔍 Run Diagnosis", type="primary", use_container_width=True)
    
    with col_clear:
        clear_button = st.button("🗑️ Clear Form", use_container_width=True)
    
    # Prepare HF band data structure
    hf_data = {
        "motor_de": vibration_motor.get("HF_DE", 0.0),
        "motor_nde": vibration_motor.get("HF_NDE", 0.0),
        "pump_de": vibration_pump.get("HF_DE", 0.0),
        "pump_nde": vibration_pump.get("HF_NDE", 0.0)
    }
    
    # Prepare demodulation data structure
    demod_data = {
        "motor_de": vibration_motor.get("Demodulation_DE", 0.0),
        "motor_nde": vibration_motor.get("Demodulation_NDE", 0.0),
        "pump_de": vibration_pump.get("Demodulation_DE", 0.0),
        "pump_nde": vibration_pump.get("Demodulation_NDE", 0.0)
    }
    
    return {
        "metadata": {
            "pump_tag": pump_tag,
            "inspector_name": inspector_name,
            "inspection_date": inspection_date,
            "location": location
        },
        "specification": spec_data,
        "vibration": {
            "motor": vibration_motor,
            "pump": vibration_pump
        },
        "operational": operational_data,
        "rpm": rpm_actual,
        "electrical": electrical_data,
        "thermal": thermal_data,
        "hf_band": hf_data,
        "demodulation": demod_data,
        "fft_motor": fft_motor,
        "fft_pump": fft_pump,
        "submit_clicked": submit_button,
        "clear_clicked": clear_button
    }
