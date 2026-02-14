"""Analisis thermal sesuai API 610 12th Ed. §11.3"""
from typing import Dict


def analyze_thermal_conditions(
    temp_motor_de: float,
    temp_motor_nde: float,
    temp_pump_de: float,
    temp_pump_nde: float,
    temp_ambient: float,
    product_type: str = "Diesel",
    lubricant_type: str = "grease"
) -> Dict:
    """
    Analisis kondisi thermal bearing sesuai API 610 §11.3
    
    Returns:
        dict: Hasil analisis thermal dengan status dan rekomendasi
    """
    # Threshold berdasarkan jenis pelumas (API 610 §11.3)
    if lubricant_type.lower() == "grease":
        warning_temp = 85
        alarm_temp = 95
        warning_rise = 40
        alarm_rise = 55
    else:  # oil lubricated
        warning_temp = 95
        alarm_temp = 105
        warning_rise = 50
        alarm_rise = 65
    
    # Hitung rise above ambient
    rise_motor_de = temp_motor_de - temp_ambient
    rise_motor_nde = temp_motor_nde - temp_ambient
    rise_pump_de = temp_pump_de - temp_ambient
    rise_pump_nde = temp_pump_nde - temp_ambient
    
    # Deteksi thermal issue
    has_issue = False
    overall_status = "NORMAL"
    recommendations = []
    
    # Critical untuk pompa gasoline/avtur (API 682 §5.4.2)
    if product_type in ["Gasoline", "Avtur", "Naphtha"] and rise_pump_nde > 40:
        has_issue = True
        overall_status = "CRITICAL"
        recommendations.append(
            f"🚨 CRITICAL: Pump NDE bearing rise {rise_pump_nde:.1f}°C > 40°C threshold for volatile products - "
            f"seal failure imminent. SHUTDOWN REQUIRED within 2 hours."
        )
    
    # General thermal assessment
    max_temp = max(temp_motor_de, temp_motor_nde, temp_pump_de, temp_pump_nde)
    max_rise = max(rise_motor_de, rise_motor_nde, rise_pump_de, rise_pump_nde)
    
    if max_temp > alarm_temp or max_rise > alarm_rise:
        has_issue = True
        if overall_status != "CRITICAL":
            overall_status = "CRITICAL"
        recommendations.append(
            f"🚨 CRITICAL: Max temperature {max_temp:.1f}°C > {alarm_temp}°C OR rise {max_rise:.1f}°C > {alarm_rise}°C - "
            f"bearing seizure imminent. SHUTDOWN REQUIRED within 2 hours."
        )
    elif max_temp > warning_temp or max_rise > warning_rise:
        has_issue = True
        if overall_status == "NORMAL":
            overall_status = "ALARM"
        recommendations.append(
            f"⚠️ WARNING: Max temperature {max_temp:.1f}°C > {warning_temp}°C OR rise {max_rise:.1f}°C > {warning_rise}°C - "
            f"check bearing lubrication & cooling. Investigate within 72 hours."
        )
    
    # Deteksi misalignment via ΔTemp DE-NDE (ISO 10816-3 Annex C)
    delta_pump = abs(temp_pump_de - temp_pump_nde)
    if delta_pump > 15:
        recommendations.append(
            f"⚠️ Pump DE-NDE temperature difference {delta_pump:.1f}°C > 15°C - possible misalignment. "
            f"Check coupling alignment."
        )
    elif delta_pump > 10:
        recommendations.append(
            f"ℹ️ Pump DE-NDE temperature difference {delta_pump:.1f}°C > 10°C - monitor for misalignment development."
        )
    
    # Default recommendation jika semua normal
    if not recommendations:
        recommendations.append("✅ Bearing temperatures within normal limits (API 610 §11.3)")
    
    return {
        "de": {
            "temperature": temp_motor_de,
            "rise_above_ambient": round(rise_motor_de, 1),
            "status": "ALARM" if temp_motor_de > alarm_temp else "WARNING" if temp_motor_de > warning_temp else "NORMAL"
        },
        "nde": {
            "temperature": temp_motor_nde,
            "rise_above_ambient": round(rise_motor_nde, 1),
            "status": "ALARM" if temp_motor_nde > alarm_temp else "WARNING" if temp_motor_nde > warning_temp else "NORMAL"
        },
        "pump_de": {
            "temperature": temp_pump_de,
            "rise_above_ambient": round(rise_pump_de, 1),
            "status": "ALARM" if temp_pump_de > alarm_temp else "WARNING" if temp_pump_de > warning_temp else "NORMAL"
        },
        "pump_nde": {
            "temperature": temp_pump_nde,
            "rise_above_ambient": round(rise_pump_nde, 1),
            "status": "ALARM" if temp_pump_nde > alarm_temp else "WARNING" if temp_pump_nde > warning_temp else "NORMAL"
        },
        "ambient": temp_ambient,
        "delta_temp_pump": round(delta_pump, 1),
        "max_temperature": round(max_temp, 1),
        "max_rise": round(max_rise, 1),
        "overall_status": overall_status,
        "recommendations": recommendations,
        "has_issue": has_issue,
        "standard": "API 610 §11.3, API 682 §5.4.2"
    }


def generate_thermal_report(thermal_data):
    """Generate laporan analisis thermal"""
    return analyze_thermal_conditions(
        temp_motor_de=thermal_data.get("temp_motor_de", 65.0),
        temp_motor_nde=thermal_data.get("temp_motor_nde", 63.0),
        temp_pump_de=thermal_data.get("temp_pump_de", 68.0),
        temp_pump_nde=thermal_data.get("temp_pump_nde", 72.0),
        temp_ambient=thermal_data.get("temp_ambient", 30.0),
        product_type=thermal_data.get("product_type", "Diesel"),
        lubricant_type=thermal_data.get("lubricant_type", "grease")
    )
