"""Modul untuk analisis data thermal (bearing temperature)"""


def analyze_thermal_conditions(temp_de, temp_nde, ambient_temp=30.0):
    """Analisis kondisi thermal bearing"""
    rise_de = temp_de - ambient_temp
    rise_nde = temp_nde - ambient_temp
    delta_temp = abs(temp_de - temp_nde)
    
    def assess_temp(temp):
        if temp > 100:
            return {"status": "CRITICAL", "risk": "SEIZURE_IMMINENT"}
        elif temp > 85:
            return {"status": "ALARM", "risk": "OVERHEAT"}
        elif temp > 80:
            return {"status": "WARNING", "risk": "OVERHEAT"}
        elif temp > 70:
            return {"status": "CAUTION", "risk": "ELEVATED"}
        else:
            return {"status": "NORMAL", "risk": "NORMAL"}
    
    de_assessment = assess_temp(temp_de)
    nde_assessment = assess_temp(temp_nde)
    
    statuses = [de_assessment["status"], nde_assessment["status"]]
    priority_order = ["NORMAL", "CAUTION", "WARNING", "ALARM", "CRITICAL"]
    overall_status = max(statuses, key=lambda s: priority_order.index(s))
    
    recommendations = []
    
    if temp_de > 80:
        recommendations.append(f"⚠️ Bearing DE temperature {temp_de}°C > 80°C - check lubrication & load")
    
    if temp_nde > 80:
        recommendations.append(f"⚠️ Bearing NDE temperature {temp_nde}°C > 80°C - check lubrication & alignment")
    
    if delta_temp > 15:
        recommendations.append(f"⚠️ Temperature difference {delta_temp}°C > 15°C - possible misalignment or unbalance")
    
    if rise_de > 50 or rise_nde > 50:
        recommendations.append("⚠️ Excessive temperature rise above ambient - check cooling & ventilation")
    
    if not recommendations:
        recommendations.append("✅ Bearing temperatures within normal range")
    
    return {
        "de": {
            "temperature": temp_de,
            "rise_above_ambient": round(rise_de, 1),
            "status": de_assessment["status"],
            "risk": de_assessment["risk"]
        },
        "nde": {
            "temperature": temp_nde,
            "rise_above_ambient": round(rise_nde, 1),
            "status": nde_assessment["status"],
            "risk": nde_assessment["risk"]
        },
        "delta_temp": round(delta_temp, 1),
        "ambient_temp": ambient_temp,
        "overall_status": overall_status,
        "recommendations": recommendations,
        "has_issue": overall_status != "NORMAL"
    }


def generate_thermal_report(thermal_data):
    """Generate laporan analisis thermal"""
    temp_de = thermal_data.get("temp_de", 65.0)
    temp_nde = thermal_data.get("temp_nde", 65.0)
    
    analysis = analyze_thermal_conditions(temp_de, temp_nde)
    
    return analysis
