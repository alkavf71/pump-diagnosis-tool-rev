"""Utility functions untuk perhitungan teknis"""
from utils.lookup_tables import PRODUCT_PROPERTIES, PUMP_SIZE_DEFAULTS, ISO_10816_3_LIMITS


def calculate_npsha(suction_kpa, product_type, temperature=None):
    """Hitung NPSHa (Net Positive Suction Head Available)"""
    rho = PRODUCT_PROPERTIES[product_type]["density_kgm3"]
    default_temp = PRODUCT_PROPERTIES[product_type]["default_temp_c"]
    temp = temperature if temperature is not None else default_temp
    
    p_vapor_m = estimate_vapor_pressure(product_type, temp)
    pressure_head = (suction_kpa + 101.3) / (9.81 * rho / 1000)
    npsha = pressure_head - p_vapor_m
    
    return round(npsha, 2)


def estimate_vapor_pressure(product_type, temperature):
    """Estimasi vapor pressure dalam meter head"""
    vapor_pressure_kpa = {
        "Gasoline": 50 + (temperature - 20) * 3,
        "Diesel": 5 + (temperature - 20) * 0.5,
        "Avtur": 20 + (temperature - 20) * 1.5,
        "Naphtha": 60 + (temperature - 20) * 4
    }
    
    rho = PRODUCT_PROPERTIES[product_type]["density_kgm3"]
    vapor_head_m = vapor_pressure_kpa[product_type] / (9.81 * rho / 1000)
    
    return round(vapor_head_m, 2)


def calculate_differential_head(discharge_kpa, suction_kpa, product_type):
    """Hitung differential head dalam meter"""
    rho = PRODUCT_PROPERTIES[product_type]["density_kgm3"]
    delta_p_kpa = discharge_kpa - suction_kpa
    head_m = delta_p_kpa / (9.81 * rho / 1000)
    return round(head_m, 2)


def calculate_voltage_imbalance(v1, v2, v3):
    """Hitung voltage imbalance percentage"""
    v_avg = (v1 + v2 + v3) / 3
    max_dev = max(abs(v1 - v_avg), abs(v2 - v_avg), abs(v3 - v_avg))
    imbalance_pct = (max_dev / v_avg) * 100
    
    status = "NORMAL" if imbalance_pct <= 2 else "WARNING" if imbalance_pct <= 5 else "ALARM"
    
    return round(imbalance_pct, 2), status


def calculate_current_imbalance(i1, i2, i3):
    """Hitung current imbalance percentage"""
    i_avg = (i1 + i2 + i3) / 3
    max_dev = max(abs(i1 - i_avg), abs(i2 - i_avg), abs(i3 - i_avg))
    imbalance_pct = (max_dev / i_avg) * 100
    
    status = "NORMAL" if imbalance_pct <= 5 else "WARNING" if imbalance_pct <= 10 else "ALARM"
    
    return round(imbalance_pct, 2), status


def calculate_load_percentage(current_avg, fla):
    """Hitung motor load percentage"""
    load_pct = (current_avg / fla) * 100
    
    if load_pct < 80:
        status = "UNDERLOAD"
    elif load_pct <= 110:
        status = "NORMAL"
    elif load_pct <= 125:
        status = "OVERLOAD_WARNING"
    else:
        status = "OVERLOAD_ALARM"
    
    return round(load_pct, 1), status


def calculate_flow_ratio(flow_rate, pump_size):
    """Hitung ratio flow terhadap BEP"""
    bep_flow = PUMP_SIZE_DEFAULTS[pump_size]["bep_flow_m3h"]
    ratio = flow_rate / bep_flow
    
    if ratio < 0.6:
        status = "RECIRCULATION_RISK"
    elif ratio > 1.2:
        status = "OVERLOAD_CAVITATION_RISK"
    else:
        status = "NORMAL"
    
    return round(ratio, 2), status


def get_zone_classification(avr_value, foundation_type="rigid"):
    """Klasifikasi zona ISO 10816-3"""
    limits = ISO_10816_3_LIMITS[foundation_type]
    
    if avr_value <= limits["zone_a_max"]:
        return "A"
    elif avr_value <= limits["zone_b_max"]:
        return "B"
    elif avr_value <= limits["zone_c_max"]:
        return "C"
    else:
        return "D"


def get_zone_description(zone):
    """Dapatkan deskripsi & rekomendasi per zona"""
    descriptions = {
        "A": {
            "name": "Normal",
            "color": "green",
            "recommendation": "Continue monitoring",
            "timeline": "Quarterly"
        },
        "B": {
            "name": "Satisfactory",
            "color": "yellow",
            "recommendation": "Investigate within 30 days",
            "timeline": "Monthly"
        },
        "C": {
            "name": "Unsatisfactory",
            "color": "orange",
            "recommendation": "Repair within 14 days",
            "timeline": "< 14 days"
        },
        "D": {
            "name": "Unacceptable",
            "color": "red",
            "recommendation": "Immediate shutdown or repair within 72 hours",
            "timeline": "< 72 hours"
        }
    }
    return descriptions.get(zone, descriptions["A"])
