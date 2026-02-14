"""Analisis listrik sesuai IEC 60034-1:2017 §4.2"""
from utils.calculations import (
    calculate_voltage_imbalance,
    calculate_current_imbalance,
    calculate_load_percentage,
    calculate_motor_slip
)
from utils.lookup_tables import PUMP_SIZE_DEFAULTS


def analyze_electrical_conditions(
    voltage_l1,
    voltage_l2,
    voltage_l3,
    current_l1,
    current_l2,
    current_l3,
    pump_size,
    rated_rpm=None,
    actual_rpm=None
):
    """Analisis kondisi listrik motor"""
    fla = PUMP_SIZE_DEFAULTS[pump_size]["fla_a"]
    
    v_imbalance, v_status = calculate_voltage_imbalance(voltage_l1, voltage_l2, voltage_l3)
    i_imbalance, i_status = calculate_current_imbalance(current_l1, current_l2, current_l3)
    
    i_avg = (current_l1 + current_l2 + current_l3) / 3
    load_pct, load_status = calculate_load_percentage(i_avg, fla)
    
    # Calculate motor slip (jika RPM data tersedia)
    slip_analysis = {"issue": False, "recommendation": "", "standard": "IEC 60034-1 §4.2"}
    if rated_rpm and actual_rpm:
        slip_analysis = calculate_motor_slip(rated_rpm, actual_rpm)
    
    # Determine overall status
    if v_status == "ALARM" or i_status == "ALARM" or load_status == "OVERLOAD_ALARM":
        overall_status = "CRITICAL"
    elif v_status == "WARNING" or i_status == "WARNING" or load_status == "OVERLOAD_WARNING" or slip_analysis.get("issue"):
        overall_status = "WARNING"
    elif load_status == "UNDERLOAD":
        overall_status = "WARNING"
    else:
        overall_status = "NORMAL"
    
    # Generate recommendations
    recommendations = []
    
    # Voltage imbalance
    if v_imbalance > 2:
        recommendations.append(f"⚠️ Voltage imbalance {v_imbalance}% > 2% - check power supply quality (IEC 60034-1)")
    
    # Current imbalance
    if i_imbalance > 5:
        recommendations.append(f"⚠️ Current imbalance {i_imbalance}% > 5% - check winding & connections (IEC 60034-1)")
    
    # Motor load
    if load_status == "OVERLOAD_WARNING":
        recommendations.append(f"⚠️ Motor load {load_pct}% > 110% FLA - check pump head & impeller")
    elif load_status == "OVERLOAD_ALARM":
        recommendations.append(f"🚨 CRITICAL: Motor load {load_pct}% > 125% FLA - immediate action required")
    elif load_status == "UNDERLOAD":
        recommendations.append(f"⚠️ Motor underload {load_pct}% < 80% FLA - check if pump operating below BEP")
    
    # Motor slip
    if slip_analysis.get("issue"):
        recommendations.append(slip_analysis["recommendation"])
    elif slip_analysis.get("recommendation"):
        recommendations.append(slip_analysis["recommendation"])
    
    # Default recommendation if all normal
    if not recommendations:
        recommendations.append("✅ Electrical parameters within normal range (IEC 60034-1)")
    
    return {
        "voltage": {
            "l1": voltage_l1,
            "l2": voltage_l2,
            "l3": voltage_l3,
            "average": round((voltage_l1 + voltage_l2 + voltage_l3) / 3, 1),
            "imbalance_pct": v_imbalance,
            "status": v_status
        },
        "current": {
            "l1": current_l1,
            "l2": current_l2,
            "l3": current_l3,
            "average": round(i_avg, 1),
            "imbalance_pct": i_imbalance,
            "status": i_status
        },
        "load": {
            "fla": fla,
            "percentage": load_pct,
            "status": load_status
        },
        "slip": slip_analysis,
        "overall_status": overall_status,
        "recommendations": recommendations,
        "has_issue": overall_status != "NORMAL",
        "standard": "IEC 60034-1 §4.2"
    }


def generate_electrical_report(electrical_data, spec_data, actual_rpm=None):
    """Generate laporan analisis listrik"""
    v1 = electrical_data.get("voltage_l1", 380.0)
    v2 = electrical_data.get("voltage_l2", 380.0)
    v3 = electrical_data.get("voltage_l3", 380.0)
    
    i1 = electrical_data.get("current_l1", 0.0)
    i2 = electrical_data.get("current_l2", 0.0)
    i3 = electrical_data.get("current_l3", 0.0)
    
    pump_size = spec_data.get("pump_size", "Medium")
    rated_rpm = spec_data.get("rated_rpm", None)
    
    analysis = analyze_electrical_conditions(
        voltage_l1=v1,
        voltage_l2=v2,
        voltage_l3=v3,
        current_l1=i1,
        current_l2=i2,
        current_l3=i3,
        pump_size=pump_size,
        rated_rpm=rated_rpm,
        actual_rpm=actual_rpm
    )
    
    return analysis
