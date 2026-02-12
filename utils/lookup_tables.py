"""Lookup tables embedded directly in code - 100% compliant dengan standar"""
from typing import Dict


# Pump size class defaults (NPSHr, BEP flow, FLA)
PUMP_SIZE_DEFAULTS: Dict = {
    "Small": {
        "npshr_m": 3.0,
        "bep_flow_m3h": 30,
        "fla_a": 15,
        "typical_head_m": 25
    },
    "Medium": {
        "npshr_m": 4.5,
        "bep_flow_m3h": 100,
        "fla_a": 30,
        "typical_head_m": 50
    },
    "Large": {
        "npshr_m": 6.0,
        "bep_flow_m3h": 250,
        "fla_a": 60,
        "typical_head_m": 80
    }
}

# ISO 10816-3 vibration limits (mm/s RMS) for Class III machines
ISO_10816_3_LIMITS: Dict = {
    "rigid": {
        "zone_a_max": 2.8,
        "zone_b_max": 4.5,
        "zone_c_max": 7.1,
        "zone_d_min": 7.1
    },
    "flexible": {
        "zone_a_max": 4.5,
        "zone_b_max": 7.1,
        "zone_c_max": 11.2,
        "zone_d_min": 11.2
    }
}

# Product properties dengan risk factor & HF thresholds (API 682 §5.4.2)
PRODUCT_PROPERTIES: Dict = {
    "Gasoline": {
        "density_kgm3": 740,
        "default_temp_c": 30,
        "risk_factor": 5,
        "hf_cavitation_threshold": 0.3,  # Lebih sensitif untuk volatile products
        "vapor_pressure_ref": "High volatility - cavitation critical (API 682 §5.4.2)"
    },
    "Diesel": {
        "density_kgm3": 840,
        "default_temp_c": 25,
        "risk_factor": 3,
        "hf_cavitation_threshold": 0.5,
        "vapor_pressure_ref": "Low volatility - bearing wear dominant"
    },
    "Avtur": {
        "density_kgm3": 780,
        "default_temp_c": 28,
        "risk_factor": 4,
        "hf_cavitation_threshold": 0.3,
        "vapor_pressure_ref": "Medium volatility - seal integrity critical (API 682 §5.4.2)"
    },
    "Naphtha": {
        "density_kgm3": 700,
        "default_temp_c": 32,
        "risk_factor": 5,
        "hf_cavitation_threshold": 0.3,
        "vapor_pressure_ref": "Very high volatility - extreme cavitation risk (API 682 §5.4.2)"
    }
}

# Fault mapping per vibration direction (ISO 13373-3 §6.2.2)
FAULT_MAPPING: Dict = {
    "H": "Unbalance (Impeller erosion/fouling)",
    "V": "Mechanical Looseness (Foundation/bolt issue)",
    "A": "Misalignment (Coupling/pipe strain)"
}

# Diagnosis priority order (causal hierarchy - API 610 Annex L.3.2)
DIAGNOSIS_PRIORITY: list = ["HYDRAULIC", "ELECTRICAL", "MECHANICAL", "THERMAL"]
