"""Engine diagnosa utama - mengintegrasikan semua analisis"""
from utils.lookup_tables import DIAGNOSIS_PRIORITY


def prioritize_diagnosis(hydraulic_report, electrical_report, mechanical_report, thermal_report):
    """Prioritaskan diagnosa berdasarkan causal hierarchy"""
    issues = {}
    
    if hydraulic_report.get("has_issue", False):
        issues["HYDRAULIC"] = {
            "report": hydraulic_report,
            "priority": DIAGNOSIS_PRIORITY.index("HYDRAULIC")
        }
    
    if electrical_report.get("has_issue", False):
        issues["ELECTRICAL"] = {
            "report": electrical_report,
            "priority": DIAGNOSIS_PRIORITY.index("ELECTRICAL")
        }
    
    if mechanical_report.get("has_issue", False):
        issues["MECHANICAL"] = {
            "report": mechanical_report,
            "priority": DIAGNOSIS_PRIORITY.index("MECHANICAL")
        }
    
    if thermal_report.get("has_issue", False):
        issues["THERMAL"] = {
            "report": thermal_report,
            "priority": DIAGNOSIS_PRIORITY.index("THERMAL")
        }
    
    sorted_issues = sorted(issues.items(), key=lambda x: x[1]["priority"])
    
    if sorted_issues:
        primary_type, primary_data = sorted_issues[0]
        primary_report = primary_data["report"]
        
        if primary_type == "HYDRAULIC":
            secondary_note = (
                "⚠️ Mechanical vibration symptoms may be secondary to hydraulic instability. "
                "Fix hydraulic issue first, then re-measure vibration."
            )
        else:
            secondary_note = None
        
        primary_diagnosis = {
            "type": primary_type,
            "report": primary_report,
            "secondary_note": secondary_note
        }
    else:
        primary_diagnosis = {
            "type": "NORMAL",
            "report": {"status": "All parameters within normal limits"},
            "secondary_note": None
        }
    
    return {
        "primary_diagnosis": primary_diagnosis,
        "all_issues": sorted_issues,
        "issue_count": len(sorted_issues),
        "has_issues": len(sorted_issues) > 0
    }


def generate_action_plan(diagnosis_result, spec_data, metadata):
    """Generate action plan berdasarkan diagnosis"""
    primary = diagnosis_result["primary_diagnosis"]
    primary_type = primary["type"]
    
    product_type = spec_data.get("product_type", "Diesel")
    pump_size = spec_data.get("pump_size", "Medium")
    pump_tag = metadata.get("pump_tag", "Unknown")
    
    risk_factor = {
        "Gasoline": 5,
        "Avtur": 4,
        "Naphtha": 5,
        "Diesel": 3
    }.get(product_type, 3)
    
    if primary_type == "NORMAL":
        risk_score = 0
        risk_level = "LOW"
        actions = [{
            "priority": "ROUTINE",
            "action": "Continue routine monitoring",
            "timeline": "Next scheduled inspection",
            "pic": "Maintenance Team"
        }]
    
    elif primary_type == "HYDRAULIC":
        report = primary["report"]
        
        if report["cavitation_risk"] == "HIGH":
            risk_score = risk_factor * 5
            risk_level = "CRITICAL"
            
            actions = [
                {
                    "priority": "IMMEDIATE",
                    "action": f"Increase suction pressure or tank level to achieve NPSHa > {report['npshr'] + 1.0} m",
                    "timeline": "< 4 hours",
                    "pic": "Operations Team",
                    "standard": "API 610 §6.3.3"
                },
                {
                    "priority": "HIGH",
                    "action": "Re-measure vibration after hydraulic correction",
                    "timeline": "24-48 hours",
                    "pic": "Vibration Analyst",
                    "standard": "ISO 10816-3"
                }
            ]
            
            if product_type in ["Gasoline", "Avtur"]:
                actions.insert(0, {
                    "priority": "CRITICAL",
                    "action": "⚠️ VOLATILE PRODUCT: Monitor seal temperature closely - risk of seal failure",
                    "timeline": "Continuous",
                    "pic": "Operations Team",
                    "standard": "API 682"
                })
        
        elif report["flow_status"] != "NORMAL":
            risk_score = risk_factor * 3
            risk_level = "HIGH"
            
            actions = [
                {
                    "priority": "HIGH",
                    "action": f"Adjust flow to 60-120% BEP ({0.6 * report['bep_flow']:.0f} - {1.2 * report['bep_flow']:.0f} m³/h)",
                    "timeline": "< 24 hours",
                    "pic": "Operations Team",
                    "standard": "API 610 Annex L"
                }
            ]
        
        else:
            risk_score = risk_factor * 2
            risk_level = "MEDIUM"
            actions = []
    
    elif primary_type == "ELECTRICAL":
        report = primary["report"]
        
        if report["overall_status"] == "CRITICAL":
            risk_score = risk_factor * 4
            risk_level = "CRITICAL"
            
            actions = [
                {
                    "priority": "IMMEDIATE",
                    "action": "Shut down motor - electrical imbalance or overload detected",
                    "timeline": "< 2 hours",
                    "pic": "Electrical Team",
                    "standard": "IEC 60034-1"
                },
                {
                    "priority": "HIGH",
                    "action": "Check power supply quality & motor winding",
                    "timeline": "< 24 hours",
                    "pic": "Electrical Team",
                    "standard": "IEEE 43"
                }
            ]
        
        elif report["overall_status"] == "WARNING":
            risk_score = risk_factor * 3
            risk_level = "HIGH"
            
            actions = [
                {
                    "priority": "HIGH",
                    "action": "Investigate voltage/current imbalance",
                    "timeline": "< 72 hours",
                    "pic": "Electrical Team",
                    "standard": "IEC 60034-1"
                }
            ]
        
        else:
            risk_score = risk_factor * 2
            risk_level = "MEDIUM"
            actions = []
    
    elif primary_type == "MECHANICAL":
        report = primary["report"]
        
        if report["overall_zone"] == "D":
            risk_score = risk_factor * 4
            risk_level = "CRITICAL"
            
            actions = [
                {
                    "priority": "IMMEDIATE",
                    "action": f"Schedule shutdown - {report['primary_fault'].lower()} detected",
                    "timeline": "< 72 hours",
                    "pic": "Maintenance Team",
                    "standard": "ISO 10816-3 Zone D"
                },
                {
                    "priority": "HIGH",
                    "action": f"Perform {report['primary_fault'].lower()} correction",
                    "timeline": "< 7 days",
                    "pic": "Maintenance Team",
                    "standard": "API 686" if "Misalignment" in report['primary_fault'] else "ISO 1940-1"
                }
            ]
        
        elif report["overall_zone"] == "C":
            risk_score = risk_factor * 3
            risk_level = "HIGH"
            
            actions = [
                {
                    "priority": "HIGH",
                    "action": f"Schedule {report['primary_fault'].lower()} correction",
                    "timeline": "< 14 days",
                    "pic": "Maintenance Team",
                    "standard": "ISO 10816-3 Zone C"
                }
            ]
        
        else:
            risk_score = risk_factor * 2
            risk_level = "MEDIUM"
            actions = []
    
    elif primary_type == "THERMAL":
        report = primary["report"]
        
        if report["overall_status"] == "CRITICAL":
            risk_score = risk_factor * 4
            risk_level = "CRITICAL"
            
            actions = [
                {
                    "priority": "IMMEDIATE",
                    "action": "Shut down pump - bearing seizure imminent",
                    "timeline": "< 2 hours",
                    "pic": "Operations Team",
                    "standard": "API 610 §11.3"
                },
                {
                    "priority": "HIGH",
                    "action": "Inspect & replace bearing if necessary",
                    "timeline": "< 24 hours",
                    "pic": "Maintenance Team",
                    "standard": "ISO 15243"
                }
            ]
        
        elif report["overall_status"] in ["ALARM", "WARNING"]:
            risk_score = risk_factor * 3
            risk_level = "HIGH"
            
            actions = [
                {
                    "priority": "HIGH",
                    "action": "Check bearing lubrication & cooling",
                    "timeline": "< 72 hours",
                    "pic": "Maintenance Team",
                    "standard": "API 610 §11.3"
                }
            ]
        
        else:
            risk_score = risk_factor * 2
            risk_level = "MEDIUM"
            actions = []
    
    else:
        risk_score = 0
        risk_level = "UNKNOWN"
        actions = []
    
    if risk_score > 0:
        actions.append({
            "priority": "ROUTINE",
            "action": "Update asset register & schedule follow-up inspection",
            "timeline": "After completion",
            "pic": "Reliability Engineer",
            "standard": "ISO 55001"
        })
    
    return {
        "risk_score": min(risk_score, 100),
        "risk_level": risk_level,
        "actions": actions,
        "primary_issue": primary_type,
        "pump_tag": pump_tag,
        "product_type": product_type
    }


def run_complete_diagnosis(input_data):
    """Jalankan diagnosa lengkap dari input data"""
    from modules.hydraulic_analysis import generate_hydraulic_report
    from modules.electrical_analysis import generate_electrical_report
    from modules.thermal_analysis import generate_thermal_report
    from modules.mechanical_analysis import analyze_mechanical_conditions
    
    spec_data = input_data["specification"]
    operational_data = input_data["operational"]
    electrical_data = input_data["electrical"]
    thermal_data = input_data["thermal"]
    vibration_data = input_data["vibration"]
    metadata = input_data["metadata"]
    
    hydraulic_report = generate_hydraulic_report(operational_data, spec_data)
    electrical_report = generate_electrical_report(electrical_data, spec_data)
    thermal_report = generate_thermal_report(thermal_data)
    
    mechanical_report = analyze_mechanical_conditions(
        vibration_data["driver"],
        vibration_data["driven"],
        spec_data["foundation_type"],
        spec_data["product_type"]
    )
    
    diagnosis_result = prioritize_diagnosis(
        hydraulic_report,
        electrical_report,
        mechanical_report,
        thermal_report
    )
    
    action_plan = generate_action_plan(diagnosis_result, spec_data, metadata)
    
    return {
        "metadata": metadata,
        "specification": spec_data,
        "analyses": {
            "hydraulic": hydraulic_report,
            "electrical": electrical_report,
            "thermal": thermal_report,
            "mechanical": mechanical_report
        },
        "diagnosis": diagnosis_result,
        "action_plan": action_plan,
        "summary": generate_summary(diagnosis_result, action_plan)
    }


def generate_summary(diagnosis_result, action_plan):
    """Generate executive summary"""
    primary = diagnosis_result["primary_diagnosis"]
    primary_type = primary["type"]
    
    if primary_type == "NORMAL":
        summary_text = "✅ **All systems normal** - Continue routine monitoring"
        color = "green"
    elif primary_type == "HYDRAULIC":
        summary_text = f"🚨 **PRIMARY ISSUE: Hydraulic** - {primary['report'].get('cavitation_status', 'Hydraulic issue detected')}"
        color = "red" if primary['report'].get('cavitation_risk') == 'HIGH' else "orange"
    elif primary_type == "ELECTRICAL":
        summary_text = f"⚡ **PRIMARY ISSUE: Electrical** - {primary['report']['overall_status']} condition detected"
        color = "red" if primary['report']['overall_status'] == 'CRITICAL' else "orange"
    elif primary_type == "MECHANICAL":
        summary_text = f"🔧 **PRIMARY ISSUE: Mechanical** - Zone {primary['report']['overall_zone']} vibration, {primary['report']['primary_fault']}"
        color = "red" if primary['report']['overall_zone'] == 'D' else "orange"
    elif primary_type == "THERMAL":
        summary_text = f"🌡️ **PRIMARY ISSUE: Thermal** - Bearing temperature {primary['report']['overall_status']}"
        color = "red" if primary['report']['overall_status'] == 'CRITICAL' else "orange"
    else:
        summary_text = "❓ **Unknown status**"
        color = "gray"
    
    return {
        "summary_text": summary_text,
        "color": color,
        "risk_level": action_plan["risk_level"],
        "risk_score": action_plan["risk_score"],
        "action_count": len(action_plan["actions"])
    }
