"""Modul untuk analisis data vibrasi"""
from utils.lookup_tables import ISO_10816_3_LIMITS, FAULT_MAPPING
from utils.calculations import get_zone_classification, get_zone_description


def calculate_average_vibration(vibration_data):
    """Hitung average per arah: Avr = (DE + NDE) / 2"""
    directions = ["H", "V", "A"]
    averages = {}
    
    for direction in directions:
        de_key = f"DE_{direction}"
        nde_key = f"NDE_{direction}"
        
        de_value = vibration_data.get(de_key, 0.0)
        nde_value = vibration_data.get(nde_key, 0.0)
        
        avg_value = (de_value + nde_value) / 2
        averages[f"Avr_{direction}"] = round(avg_value, 2)
    
    averages["Overall_Max"] = max(averages.values())
    
    return averages


def classify_vibration_zones(averages, foundation_type="rigid"):
    """Klasifikasikan zona ISO 10816-3 per arah"""
    zones = {}
    directions = ["H", "V", "A"]
    
    for direction in directions:
        avg_key = f"Avr_{direction}"
        avg_value = averages.get(avg_key, 0.0)
        
        zone = get_zone_classification(avg_value, foundation_type)
        zone_desc = get_zone_description(zone)
        
        zones[f"Zone_{direction}"] = {
            "zone": zone,
            "name": zone_desc["name"],
            "color": zone_desc["color"],
            "recommendation": zone_desc["recommendation"]
        }
    
    return zones


def identify_fault_indicators(averages):
    """Identifikasi kemungkinan fault berdasarkan arah dominan"""
    directions = ["H", "V", "A"]
    faults = {}
    
    max_direction = max(directions, key=lambda d: averages.get(f"Avr_{d}", 0))
    primary_fault = FAULT_MAPPING[max_direction]
    
    faults["primary_fault"] = primary_fault
    faults["primary_direction"] = max_direction
    
    for direction in directions:
        avg_key = f"Avr_{direction}"
        avg_value = averages.get(avg_key, 0.0)
        
        fault_type = FAULT_MAPPING[direction]
        faults[f"fault_{direction}"] = {
            "type": fault_type,
            "confidence": "HIGH" if avg_value > 4.5 else "MEDIUM" if avg_value > 2.8 else "LOW"
        }
    
    return faults


def analyze_hf_vibration(vibration_data, product_type):
    """Analisis high-frequency vibration untuk cavitation & bearing defect"""
    hf_value = vibration_data.get("HF_5_16kHz", 0.0)
    demod_value = vibration_data.get("Demodulation", 0.0)
    
    if product_type in ["Gasoline", "Avtur", "Naphtha"]:
        cavitation_threshold = 0.3
    else:
        cavitation_threshold = 0.5
    
    analysis = {
        "hf_value": hf_value,
        "demod_value": demod_value,
        "cavitation_risk": "HIGH" if hf_value > cavitation_threshold else "LOW",
        "bearing_defect_risk": "HIGH" if demod_value > 0.5 else "LOW",
        "recommendation": ""
    }
    
    if hf_value > cavitation_threshold:
        analysis["recommendation"] = "⚠️ High-frequency vibration indicates cavitation risk. Verify NPSHa."
    elif demod_value > 0.5:
        analysis["recommendation"] = "⚠️ Demodulation signal indicates early bearing defect."
    else:
        analysis["recommendation"] = "✅ HF vibration within normal range."
    
    return analysis


def generate_vibration_report(vibration_data, foundation_type="rigid", product_type="Diesel"):
    """Generate laporan lengkap analisis vibrasi"""
    averages = calculate_average_vibration(vibration_data)
    zones = classify_vibration_zones(averages, foundation_type)
    faults = identify_fault_indicators(averages)
    hf_analysis = analyze_hf_vibration(vibration_data, product_type)
    
    overall_zone = max(
        [zones[f"Zone_{d}"]["zone"] for d in ["H", "V", "A"]],
        key=lambda z: ["A", "B", "C", "D"].index(z)
    )
    
    return {
        "averages": averages,
        "zones": zones,
        "faults": faults,
        "hf_analysis": hf_analysis,
        "overall_zone": overall_zone,
        "severity": get_zone_description(overall_zone)["name"],
        "recommendation": get_zone_description(overall_zone)["recommendation"]
    }
