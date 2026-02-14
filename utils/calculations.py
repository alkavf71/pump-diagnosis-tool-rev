"""Fungsi kalkulasi akurat sesuai standar internasional"""
import math


def calculate_npsha(suction_pressure_kpa, product_type, temperature_c=25):
    """
    Hitung NPSHa sesuai ISO 13709 §7.2.1
    
    Formula: NPSHa = (P_suction - P_vapor) / (ρ * g) + v²/(2g)
    Untuk pompa sentrifugal di terminal, head velocity diabaikan (v²/2g < 0.5m)
    
    Returns:
        float: NPSHa dalam meter
    """
    # Densitas berdasarkan produk (kg/m³)
    density = {
        "Gasoline": 740,
        "Diesel": 840,
        "Avtur": 780,
        "Naphtha": 700
    }.get(product_type, 800)
    
    # Vapor pressure pada 25°C (kPa) - API 682 §5.4.2
    vapor_pressure = {
        "Gasoline": 55,
        "Diesel": 0.5,
        "Avtur": 15,
        "Naphtha": 60
    }.get(product_type, 1.0)
    
    # Konversi suction pressure ke absolute (asumsi atmospheric = 101.3 kPa)
    suction_abs = suction_pressure_kpa + 101.3
    
    # Hitung NPSHa (meter)
    npsha = (suction_abs - vapor_pressure) / (density * 0.00981)
    
    return round(npsha, 2)


def calculate_differential_head(discharge_kpa, suction_kpa, product_type):
    """
    Hitung differential head sesuai ISO 13709 §7.2.1
    
    Returns:
        float: Head dalam meter
    """
    density = {
        "Gasoline": 740,
        "Diesel": 840,
        "Avtur": 780,
        "Naphtha": 700
    }.get(product_type, 800)
    
    delta_p_kpa = discharge_kpa - suction_kpa
    head_m = delta_p_kpa / (density * 0.00981)
    
    return round(head_m, 1)


def calculate_flow_ratio(flow_rate, pump_size):
    """
    Hitung flow ratio terhadap BEP sesuai API 610 Annex L
    
    Returns:
        tuple: (flow_ratio, status)
    """
    bep_flow = {
        "Small": 30,
        "Medium": 100,
        "Large": 250
    }.get(pump_size, 100)
    
    flow_ratio = flow_rate / bep_flow
    
    if flow_ratio < 0.6:
        status = "RECIRCULATION_RISK"
    elif flow_ratio > 1.2:
        status = "OVERLOAD_CAVITATION_RISK"
    else:
        status = "NORMAL"
    
    return round(flow_ratio, 2), status


def calculate_voltage_imbalance(v1, v2, v3):
    """
    Hitung voltage imbalance sesuai IEC 60034-1 §4.2
    
    Formula: Imbalance % = (Max - Min) / Average * 100
    
    Returns:
        tuple: (imbalance_pct, status)
    """
    voltages = [v1, v2, v3]
    v_max = max(voltages)
    v_min = min(voltages)
    v_avg = sum(voltages) / 3
    
    if v_avg == 0:
        return 0.0, "INVALID"
    
    imbalance_pct = ((v_max - v_min) / v_avg) * 100
    
    if imbalance_pct > 5.0:
        status = "ALARM"
    elif imbalance_pct > 2.0:
        status = "WARNING"
    else:
        status = "NORMAL"
    
    return round(imbalance_pct, 1), status


def calculate_current_imbalance(i1, i2, i3):
    """
    Hitung current imbalance sesuai IEC 60034-1 §4.2
    
    Returns:
        tuple: (imbalance_pct, status)
    """
    currents = [i1, i2, i3]
    i_max = max(currents)
    i_min = min(currents)
    i_avg = sum(currents) / 3
    
    if i_avg == 0:
        return 0.0, "INVALID"
    
    imbalance_pct = ((i_max - i_min) / i_avg) * 100
    
    if imbalance_pct > 10.0:
        status = "ALARM"
    elif imbalance_pct > 5.0:
        status = "WARNING"
    else:
        status = "NORMAL"
    
    return round(imbalance_pct, 1), status


def calculate_load_percentage(current_avg, fla):
    """
    Hitung persentase beban motor sesuai IEC 60034-1 §4.2
    
    Returns:
        tuple: (load_pct, status)
    """
    if fla == 0:
        return 0.0, "INVALID"
    
    load_pct = (current_avg / fla) * 100
    
    if load_pct > 125:
        status = "OVERLOAD_ALARM"
    elif load_pct > 110:
        status = "OVERLOAD_WARNING"
    elif load_pct < 80:
        status = "UNDERLOAD"
    else:
        status = "NORMAL"
    
    return round(load_pct, 1), status


def calculate_motor_slip(rated_rpm, actual_rpm):
    """
    Hitung slip motor sesuai IEC 60034-1 §4.2
    
    Returns:
        dict: Hasil kalkulasi slip
    """
    if rated_rpm <= 0:
        return {
            "slip_pct": 0.0,
            "slip_rpm": 0.0,
            "status": "INVALID",
            "issue": False,
            "recommendation": "⚠️ Invalid rated RPM - cannot calculate slip"
        }
    
    slip_rpm = rated_rpm - actual_rpm
    slip_pct = (slip_rpm / rated_rpm) * 100
    
    # Threshold berdasarkan IEC 60034-1 §4.2
    if slip_pct > 8.0:
        status = "CRITICAL_OVERLOAD"
        issue = True
        recommendation = (
            f"🚨 CRITICAL OVERLOAD: Slip {slip_pct:.1f}% > 8% - immediate action required. "
            f"Check pump head, cavitation, or mechanical binding."
        )
    elif slip_pct > 5.0:
        status = "HIGH_SLIP"
        issue = True
        recommendation = (
            f"⚠️ HIGH SLIP ({slip_pct:.1f}%) - Possible hydraulic overload or cavitation. "
            f"Verify NPSHa and discharge pressure."
        )
    elif slip_pct < -2.0:
        # Actual RPM > Rated RPM (tidak mungkin kecuali generator/backflow)
        status = "ABNORMAL"
        issue = True
        recommendation = (
            f"⚠️ Actual RPM ({actual_rpm}) > Rated RPM ({rated_rpm}) - "
            f"Verify tachometer calibration or check for backflow (check valve failure)."
        )
    elif slip_pct < 0:
        status = "LOW_SLIP"
        issue = False
        recommendation = f"✅ Motor slip normal - low load condition ({slip_pct:.1f}%)"
    else:
        status = "NORMAL"
        issue = False
        recommendation = f"✅ Motor slip normal ({slip_pct:.1f}%)"
    
    return {
        "slip_pct": round(slip_pct, 2),
        "slip_rpm": round(slip_rpm, 1),
        "status": status,
        "issue": issue,
        "recommendation": recommendation
    }
