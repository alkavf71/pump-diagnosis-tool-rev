"""Modul untuk analisis kondisi mechanical (agregasi dari vibrasi)"""
from modules.vibration_analysis import generate_vibration_report


def analyze_mechanical_conditions(
    vibration_driver,
    vibration_driven,
    foundation_type="rigid",
    product_type="Diesel"
):
    """Analisis kondisi mechanical pompa & motor"""
    driver_report = generate_vibration_report(vibration_driver, foundation_type, product_type)
    driven_report = generate_vibration_report(vibration_driven, foundation_type, product_type)
    
    driver_max = driver_report["averages"]["Overall_Max"]
    driven_max = driven_report["averages"]["Overall_Max"]
    
    if driver_max > driven_max:
        primary_component = "Motor (Driver)"
        primary_component_report = driver_report
    else:
        primary_component = "Pump (Driven)"
        primary_component_report = driven_report
    
    overall_zone = max(
        driver_report["overall_zone"],
        driven_report["overall_zone"],
        key=lambda z: ["A", "B", "C", "D"].index(z)
    )
    
    recommendations = []
    
    # === FIX KRUSIAL: Hanya diagnosa fault jika vibrasi signifikan (> 2.8 mm/s) ===
    if overall_zone in ["C", "D"]:
        if driver_report["overall_zone"] in ["C", "D"]:
            recommendations.append(f"⚠️ Motor vibration Zone {driver_report['overall_zone']} - check coupling alignment & rotor balance")
        
        if driven_report["overall_zone"] in ["C", "D"]:
            recommendations.append(f"⚠️ Pump vibration Zone {driven_report['overall_zone']} - check impeller balance & bearing condition")
        
        # Identifikasi fault spesifik hanya jika vibrasi > 2.8 mm/s
        primary_fault = primary_component_report["faults"]["primary_fault"]
        if driver_max > 2.8:
            if "Unbalance" in primary_fault:
                recommendations.append("🔧 Primary fault: Unbalance - perform dynamic balancing")
            elif "Misalignment" in primary_fault:
                recommendations.append("🔧 Primary fault: Misalignment - perform laser alignment")
            elif "Looseness" in primary_fault:
                recommendations.append("🔧 Primary fault: Mechanical looseness - check foundation bolts & grouting")
    else:
        # Vibrasi normal (Zone A/B) - TIDAK ADA fault spesifik
        recommendations.append("✅ Mechanical vibration within acceptable limits")
        primary_fault = "None (Vibration Normal)"
    
    return {
        "driver": driver_report,
        "driven": driven_report,
        "primary_component": primary_component,
        "overall_zone": overall_zone,
        "overall_severity": primary_component_report["severity"],
        "primary_fault": primary_fault,  # ← FIX: "None" untuk vibrasi normal
        "recommendations": recommendations,
        "has_issue": overall_zone in ["C", "D"]
    }
