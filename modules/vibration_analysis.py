"""Analisis vibrasi sesuai ISO 10816-3:2022"""
from utils.lookup_tables import ISO_10816_3_LIMITS, FAULT_MAPPING


def get_iso_zone(vibration_value, foundation_type):
    """
    Tentukan zona ISO 10816-3 berdasarkan nilai vibrasi
    
    Returns:
        str: "A", "B", "C", atau "D"
    """
    foundation_type = foundation_type.lower()
    limits = ISO_10816_3_LIMITS.get(foundation_type, ISO_10816_3_LIMITS["rigid"])
    
    if vibration_value <= limits["zone_a_max"]:
        return "A"
    elif vibration_value <= limits["zone_b_max"]:
        return "B"
    elif vibration_value <= limits["zone_c_max"]:
        return "C"
    else:
        return "D"


def calculate_directional_averages(vibration_data):
    """
    Hitung rata-rata per arah (H/V/A) dari DE + NDE
    
    Returns:
        dict: {"H": avg, "V": avg, "A": avg, "Overall_Max": max_value}
    """
    avg_h = (vibration_data.get("DE_H", 0.0) + vibration_data.get("NDE_H", 0.0)) / 2
    avg_v = (vibration_data.get("DE_V", 0.0) + vibration_data.get("NDE_V", 0.0)) / 2
    avg_a = (vibration_data.get("DE_A", 0.0) + vibration_data.get("NDE_A", 0.0)) / 2
    
    overall_max = max(avg_h, avg_v, avg_a)
    
    return {
        "Avr_H": round(avg_h, 2),
        "Avr_V": round(avg_v, 2),
        "Avr_A": round(avg_a, 2),
        "Overall_Max": round(overall_max, 2)
    }


def analyze_fault_patterns(fft_peaks, rpm_actual):
    """
    Analisis pola harmonik untuk identifikasi fault (ISO 13373-3 Table 2)
    
    Returns:
        dict: Primary fault dan confidence
    """
    if rpm_actual <= 0 or not fft_peaks:
        return {"primary_fault": "Unknown", "confidence": "LOW"}
    
    rpm_hz = rpm_actual / 60.0
    harmonics = {}
    
    # Ekstrak harmonik dari semua peak
    for peak in fft_peaks:
        if peak["frequency_hz"] > 0.5 and peak["amplitude_mms"] > 0.5:
            ratio = peak["frequency_hz"] / rpm_hz
            order = round(ratio)
            
            if 0.95 <= ratio <= 4.05:  # Harmonik 1x-4x RPM
                if order not in harmonics:
                    harmonics[order] = []
                harmonics[order].append({
                    "freq": peak["frequency_hz"],
                    "amp": peak["amplitude_mms"],
                    "ratio": ratio,
                    "dir": peak.get("direction", "H")
                })
    
    # Deteksi fault berdasarkan pola harmonik
    has_1x = 1 in harmonics and max(p["amp"] for p in harmonics[1]) > 1.0
    has_2x = 2 in harmonics and max(p["amp"] for p in harmonics[2]) > 1.5
    has_3x = 3 in harmonics and max(p["amp"] for p in harmonics[3]) > 0.7
    
    # Analisis directional dominance
    axial_2x = any(p["dir"] == "A" and abs(p["ratio"] - 2.0) < 0.05 for h in harmonics.get(2, []) for p in [h])
    horiz_1x = any(p["dir"] == "H" and abs(p["ratio"] - 1.0) < 0.05 for h in harmonics.get(1, []) for p in [h])
    
    # Decision logic
    if has_3x and (has_1x or has_2x):
        return {"primary_fault": "Mechanical Looseness", "confidence": "HIGH"}
    elif axial_2x and has_2x:
        return {"primary_fault": "Misalignment", "confidence": "HIGH"}
    elif horiz_1x and has_1x and not has_2x:
        return {"primary_fault": "Unbalance", "confidence": "HIGH"}
    elif has_1x and has_2x:
        return {"primary_fault": "Unbalance with Misalignment", "confidence": "MEDIUM"}
    else:
        return {"primary_fault": "Unknown", "confidence": "LOW"}
