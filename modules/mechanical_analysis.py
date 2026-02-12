"""Modul untuk analisis kondisi mechanical (vibrasi + demodulation bearing defect)"""
from modules.vibration_analysis import generate_vibration_report


def analyze_mechanical_conditions(
    vibration_driver,
    vibration_driven,
    foundation_type="rigid",
    product_type="Diesel"
):
    """
    Analisis kondisi mechanical pompa & motor + demodulation-based bearing defect detection
    
    ISO 15243:2017 §5.2:
    "Demodulation analysis shall be used for early stage (Stage 1) bearing defect detection 
     when overall vibration levels are still within acceptable limits."
    """
    driver_report = generate_vibration_report(vibration_driver, foundation_type, product_type)
    driven_report = generate_vibration_report(vibration_driven, foundation_type, product_type)
    
    driver_max = driver_report["averages"]["Overall_Max"]
    driven_max = driven_report["averages"]["Overall_Max"]
    
    # === KRUSIAL: Demodulation-based bearing defect detection (ISO 15243 §5.2) ===
    demod_driver = vibration_driver.get("Demodulation", 0.0)
    demod_driven = vibration_driven.get("Demodulation", 0.0)
    demod_max = max(demod_driver, demod_driven)
    
    bearing_defect_risk = "HIGH" if demod_max > 0.5 else "MEDIUM" if demod_max > 0.3 else "LOW"
    bearing_defect_status = (
        f"⚠️ Demodulation {demod_max:.2f}g > 0.5g - early bearing defect detected (ISO 15243 §5.2)"
        if bearing_defect_risk == "HIGH"
        else f"✅ Demodulation {demod_max:.2f}g within normal range"
    )
    
    # Tentukan primary component
    if driver_max > driven_max:
        primary_component = "Motor (Driver)"
        primary_component_report = driver_report
    else:
        primary_component = "Pump (Driven)"
        primary_component_report = driven_report
    
    # Tentukan overall zone
    overall_zone = max(
        driver_report["overall_zone"],
        driven_report["overall_zone"],
        key=lambda z: ["A", "B", "C", "D"].index(z)
    )
    
    recommendations = []
    
    # === FIX KRUSIAL: Vibrasi 0.0 TIDAK BOLEH diagnosa "unbalance" ===
    # ISO 10816-3: Zone A = normal operation, TIDAK ADA fault spesifik
    if overall_zone in ["A", "B"] and driver_max <= 2.8 and driven_max <= 2.8:
        # Vibrasi normal - TIDAK ADA fault spesifik
        recommendations.append("✅ Mechanical vibration within acceptable limits (ISO 10816-3 Zone A/B)")
        primary_fault = "None (Vibration Normal)"
        has_issue = bearing_defect_risk == "HIGH"  # Hanya bearing defect yang trigger issue di Zone A/B
    else:
        # Vibrasi tinggi (Zone C/D) - perlu investigasi
        if driver_report["overall_zone"] in ["C", "D"]:
            recommendations.append(f"⚠️ Motor vibration Zone {driver_report['overall_zone']} - check coupling alignment & rotor balance")
        
        if driven_report["overall_zone"] in ["C", "D"]:
            recommendations.append(f"⚠️ Pump vibration Zone {driven_report['overall_zone']} - check impeller balance & bearing condition")
        
        # Identifikasi fault spesifik hanya jika vibrasi > 2.8 mm/s
        primary_fault = primary_component_report["faults"]["primary_fault"]
        if driver_max > 2.8:
            if "Unbalance" in primary_fault:
                recommendations.append("🔧 Primary fault: Unbalance - perform dynamic balancing (ISO 1940-1)")
            elif "Misalignment" in primary_fault:
                recommendations.append("🔧 Primary fault: Misalignment - perform laser alignment (API 686)")
            elif "Looseness" in primary_fault:
                recommendations.append("🔧 Primary fault: Mechanical looseness - check foundation bolts & grouting")
        
        has_issue = True
    
    # === Tambahkan bearing defect warning ke recommendations ===
    if bearing_defect_risk in ["HIGH", "MEDIUM"] and demod_max > 0.3:
        recommendations.insert(0, 
            f"⚠️ Bearing defect risk ({bearing_defect_risk}): "
            f"Demodulation = {demod_max:.2f}g - schedule bearing inspection within 7 days (ISO 15243 §5.2)"
        )
        has_issue = True  # Demodulasi tinggi = issue meskipun vibrasi normal
    
    return {
        "driver": driver_report,
        "driven": driven_report,
        "primary_component": primary_component,
        "overall_zone": overall_zone,
        "overall_severity": primary_component_report["severity"],
        "primary_fault": primary_fault,
        "bearing_defect_risk": bearing_defect_risk,
        "bearing_defect_status": bearing_defect_status,
        "demod_max": round(demod_max, 2),
        "recommendations": recommendations,
        "has_issue": has_issue,
        "standard": "ISO 10816-3, ISO 15243 §5.2"
    }
