"""Analisis mekanikal sesuai ISO 13373-3:2020 & ISO 15243:2017"""
from modules.vibration_analysis import (
    get_iso_zone,
    calculate_directional_averages,
    analyze_fault_patterns
)
from utils.lookup_tables import FAULT_MAPPING


def analyze_mechanical_conditions(
    vibration_motor,
    vibration_pump,
    foundation_type="rigid",
    product_type="Diesel"
):
    """
    Analisis kondisi mekanikal pompa & motor + demodulation-based bearing defect detection
    
    ISO 15243:2017 §5.2:
    "Demodulation analysis shall be used for early stage (Stage 1) bearing defect detection 
     when overall vibration levels are still within acceptable limits."
    """
    # Hitung averages untuk motor & pompa
    motor_averages = calculate_directional_averages(vibration_motor)
    pump_averages = calculate_directional_averages(vibration_pump)
    
    motor_max = motor_averages["Overall_Max"]
    pump_max = pump_averages["Overall_Max"]
    
    # Tentukan primary component
    if pump_max > motor_max:
        primary_component = "Pump (Driven)"
        primary_averages = pump_averages
    else:
        primary_component = "Motor (Driver)"
        primary_averages = motor_averages
    
    # Tentukan overall zone
    motor_zone = get_iso_zone(motor_max, foundation_type)
    pump_zone = get_iso_zone(pump_max, foundation_type)
    overall_zone = max(motor_zone, pump_zone, key=lambda z: ["A", "B", "C", "D"].index(z))
    
    # === KRUSIAL: Demodulation-based bearing defect detection (ISO 15243 §5.2) ===
    demod_motor_de = vibration_motor.get("Demodulation_DE", 0.0)
    demod_motor_nde = vibration_motor.get("Demodulation_NDE", 0.0)
    demod_pump_de = vibration_pump.get("Demodulation_DE", 0.0)
    demod_pump_nde = vibration_pump.get("Demodulation_NDE", 0.0)
    
    demod_max = max(demod_motor_de, demod_motor_nde, demod_pump_de, demod_pump_nde)
    
    bearing_defect_risk = "HIGH" if demod_max > 0.5 else "MEDIUM" if demod_max > 0.3 else "LOW"
    bearing_defect_status = (
        f"⚠️ Demodulation {demod_max:.2f}g > 0.5g - early bearing defect detected (ISO 15243 §5.2)"
        if bearing_defect_risk == "HIGH"
        else f"✅ Demodulation {demod_max:.2f}g within normal range"
    )
    
    recommendations = []
    
    # === FIX KRUSIAL: Vibrasi 0.0 TIDAK BOLEH diagnosa "unbalance" ===
    if overall_zone in ["A", "B"] and motor_max <= 2.8 and pump_max <= 2.8:
        # Vibrasi normal - TIDAK ADA fault spesifik
        recommendations.append("✅ Mechanical vibration within acceptable limits (ISO 10816-3 Zone A/B)")
        primary_fault = "None (Vibration Normal)"
        has_issue = bearing_defect_risk == "HIGH"  # Hanya bearing defect yang trigger issue di Zone A/B
    else:
        # Vibrasi tinggi (Zone C/D) - perlu investigasi
        if motor_zone in ["C", "D"]:
            recommendations.append(f"⚠️ Motor vibration Zone {motor_zone} - check coupling alignment & rotor balance")
        
        if pump_zone in ["C", "D"]:
            recommendations.append(f"⚠️ Pump vibration Zone {pump_zone} - check impeller balance & bearing condition")
        
        # Identifikasi fault spesifik hanya jika vibrasi > 2.8 mm/s
        primary_fault = "Multiple Issues Detected"
        if pump_max > 2.8:
            # Analisis FFT pattern jika tersedia
            fft_peaks = []
            if "FFT_DE_H_Freq1" in vibration_pump:
                for i in range(1, 4):
                    freq_key = f"FFT_DE_H_Freq{i}"
                    amp_key = f"FFT_DE_H_Amp{i}"
                    if freq_key in vibration_pump and vibration_pump[freq_key] > 0.5:
                        fft_peaks.append({
                            "frequency_hz": vibration_pump[freq_key],
                            "amplitude_mms": vibration_pump.get(amp_key, 0.0),
                            "direction": "H"
                        })
            
            fault_analysis = analyze_fault_patterns(fft_peaks, vibration_pump.get("RPM", 2950))
            primary_fault = fault_analysis["primary_fault"]
            
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
        "motor": {
            "averages": motor_averages,
            "overall_zone": motor_zone,
            "demod_de": round(demod_motor_de, 2),
            "demod_nde": round(demod_motor_nde, 2)
        },
        "pump": {
            "averages": pump_averages,
            "overall_zone": pump_zone,
            "demod_de": round(demod_pump_de, 2),
            "demod_nde": round(demod_pump_nde, 2)
        },
        "primary_component": primary_component,
        "overall_zone": overall_zone,
        "primary_fault": primary_fault,
        "bearing_defect_risk": bearing_defect_risk,
        "bearing_defect_status": bearing_defect_status,
        "demod_max": round(demod_max, 2),
        "recommendations": recommendations,
        "has_issue": has_issue,
        "standard": "ISO 10816-3, ISO 13373-3 §6.2.2, ISO 15243 §5.2"
    }
