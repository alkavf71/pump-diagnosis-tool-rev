"""Modul untuk analisis data hidraulis (NPSHa, BEP, dll)"""
from utils.calculations import (
    calculate_npsha,
    calculate_differential_head,
    calculate_flow_ratio
)
from utils.lookup_tables import PUMP_SIZE_DEFAULTS


def analyze_hydraulic_conditions(
    suction_pressure,
    discharge_pressure,
    flow_rate,
    product_type,
    pump_size,
    temperature=None
):
    """Analisis kondisi hidraulis pompa"""
    npshr = PUMP_SIZE_DEFAULTS[pump_size]["npshr_m"]
    bep_flow = PUMP_SIZE_DEFAULTS[pump_size]["bep_flow_m3h"]
    
    npsha = calculate_npsha(suction_pressure, product_type, temperature)
    head = calculate_differential_head(discharge_pressure, suction_pressure, product_type)
    flow_ratio, flow_status = calculate_flow_ratio(flow_rate, pump_size)
    
    safety_margin = 1.0
    npsha_margin = npsha - (npshr + safety_margin)
    
    if npsha_margin < 0:
        cavitation_risk = "HIGH"
        cavitation_status = "⚠️ CRITICAL: NPSHa < NPSHr + safety margin"
    elif npsha_margin < 1.0:
        cavitation_risk = "MEDIUM"
        cavitation_status = "⚠️ WARNING: Low NPSHa margin"
    else:
        cavitation_risk = "LOW"
        cavitation_status = "✅ NPSHa adequate"
    
    if flow_status == "RECIRCULATION_RISK":
        flow_recommendation = "⚠️ Flow < 60% BEP - risk of recirculation & vibration"
    elif flow_status == "OVERLOAD_CAVITATION_RISK":
        flow_recommendation = "⚠️ Flow > 120% BEP - risk of cavitation & overload"
    else:
        flow_recommendation = "✅ Flow within acceptable range"
    
    return {
        "npsha": npsha,
        "npshr": npshr,
        "npsha_margin": round(npsha_margin, 2),
        "cavitation_risk": cavitation_risk,
        "cavitation_status": cavitation_status,
        "head": head,
        "flow_rate": flow_rate,
        "bep_flow": bep_flow,
        "flow_ratio": flow_ratio,
        "flow_status": flow_status,
        "flow_recommendation": flow_recommendation,
        "has_issue": cavitation_risk != "LOW" or flow_status != "NORMAL"
    }


def generate_hydraulic_report(operational_data, spec_data):
    """Generate laporan analisis hidraulis"""
    suction = operational_data.get("suction_pressure", 0.0)
    discharge = operational_data.get("discharge_pressure", 0.0)
    flow = operational_data.get("flow_rate", 0.0)
    
    product = spec_data.get("product_type", "Diesel")
    pump_size = spec_data.get("pump_size", "Medium")
    
    analysis = analyze_hydraulic_conditions(
        suction_pressure=suction,
        discharge_pressure=discharge,
        flow_rate=flow,
        product_type=product,
        pump_size=pump_size
    )
    
    return analysis
