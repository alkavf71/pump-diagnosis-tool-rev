"""Analisis hidraulis sesuai API 610 12th Ed. §6.3.3 & Annex L"""
from utils.calculations import (
    calculate_npsha,
    calculate_differential_head,
    calculate_flow_ratio
)
from utils.lookup_tables import PUMP_SIZE_DEFAULTS, PRODUCT_PROPERTIES


def analyze_hydraulic_conditions(
    suction_pressure,
    discharge_pressure,
    flow_rate,
    product_type,
    pump_size,
    hf_5_16khz_motor_de=0.0,
    hf_5_16khz_motor_nde=0.0,
    hf_5_16khz_pump_de=0.0,
    hf_5_16khz_pump_nde=0.0
):
    """
    Analisis kondisi hidraulis pompa + HF-based cavitation detection
    
    API 610 12th Ed. §6.3.3:
    "Monitor high-frequency vibration (5-16 kHz) as independent cavitation indicator — 
     independent of overall RMS vibration and NPSHa calculation."
    """
    npshr = PUMP_SIZE_DEFAULTS[pump_size]["npshr_m"]
    bep_flow = PUMP_SIZE_DEFAULTS[pump_size]["bep_flow_m3h"]
    
    # Hitung NPSHa
    npsha = calculate_npsha(suction_pressure, product_type)
    head = calculate_differential_head(discharge_pressure, suction_pressure, product_type)
    flow_ratio, flow_status = calculate_flow_ratio(flow_rate, pump_size)
    
    # === KRUSIAL: HF-BASED CAVITATION DETECTION (API 610 §6.3.3) ===
    hf_max = max(
        hf_5_16khz_motor_de,
        hf_5_16khz_motor_nde,
        hf_5_16khz_pump_de,
        hf_5_16khz_pump_nde
    )
    
    # Threshold berbasis produk (API 682 §5.4.2: stricter for volatile hydrocarbons)
    cavitation_threshold = PRODUCT_PROPERTIES[product_type]["hf_cavitation_threshold"]
    
    hf_cavitation_risk = "HIGH" if hf_max > cavitation_threshold else "LOW"
    hf_cavitation_status = (
        f"⚠️ HF vibration {hf_max:.2f}g > {cavitation_threshold}g threshold - cavitation likely"
        if hf_cavitation_risk == "HIGH"
        else f"✅ HF vibration {hf_max:.2f}g within normal range"
    )
    
    # Safety margin untuk NPSHa (API 610 recommendation)
    safety_margin = 1.0
    npsha_margin = npsha - (npshr + safety_margin)
    
    # === COMBINE HF + NPSHa UNTUK HYDRAULIC ISSUE DETECTION ===
    has_hydraulic_issue = False
    cavitation_risk = "LOW"
    cavitation_status = ""
    
    if hf_cavitation_risk == "HIGH" and npsha_margin < 1.0:
        # HF + low NPSHa = CONFIRMED cavitation (API 610 §6.3.3)
        has_hydraulic_issue = True
        cavitation_risk = "HIGH"
        cavitation_status = f"🚨 CONFIRMED CAVITATION: HF={hf_max:.2f}g + NPSHa margin={npsha_margin:.2f}m"
    elif hf_cavitation_risk == "HIGH":
        # HF tinggi tapi NPSHa OK = SUSPECTED cavitation (early stage)
        has_hydraulic_issue = True
        cavitation_risk = "MEDIUM"
        cavitation_status = f"⚠️ SUSPECTED CAVITATION: HF={hf_max:.2f}g (verify suction conditions)"
    elif npsha_margin < 0:
        # NPSHa rendah tanpa HF tinggi = potential cavitation
        has_hydraulic_issue = True
        cavitation_risk = "MEDIUM"
        cavitation_status = f"⚠️ LOW NPSHa margin ({npsha_margin:.2f}m) - cavitation risk"
    else:
        cavitation_risk = "LOW"
        cavitation_status = "✅ NPSHa adequate + HF normal"
    
    # Flow status assessment
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
        "hf_cavitation_risk": hf_cavitation_risk,
        "hf_cavitation_status": hf_cavitation_status,
        "hf_max": round(hf_max, 2),
        "hf_motor_de": round(hf_5_16khz_motor_de, 2),
        "hf_motor_nde": round(hf_5_16khz_motor_nde, 2),
        "hf_pump_de": round(hf_5_16khz_pump_de, 2),
        "hf_pump_nde": round(hf_5_16khz_pump_nde, 2),
        "head": head,
        "flow_rate": flow_rate,
        "bep_flow": bep_flow,
        "flow_ratio": flow_ratio,
        "flow_status": flow_status,
        "flow_recommendation": flow_recommendation,
        "has_issue": has_hydraulic_issue,
        "standard": "API 610 §6.3.3, API 682 §5.4.2"
    }


def generate_hydraulic_report(operational_data, spec_data, hf_data):
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
        pump_size=pump_size,
        hf_5_16khz_motor_de=hf_data.get("motor_de", 0.0),
        hf_5_16khz_motor_nde=hf_data.get("motor_nde", 0.0),
        hf_5_16khz_pump_de=hf_data.get("pump_de", 0.0),
        hf_5_16khz_pump_nde=hf_data.get("pump_nde", 0.0)
    )
    
    return analysis
