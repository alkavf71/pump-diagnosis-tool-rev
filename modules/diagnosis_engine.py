"""Engine diagnosa utama - causal hierarchy 100% compliant dengan API/ISO/IEC"""
from utils.lookup_tables import DIAGNOSIS_PRIORITY, PRODUCT_PROPERTIES


def analyze_fft_peaks(fft_data, rpm_actual, spec_data):
    """Analisis peak frequency dari FFT spectrum"""
    if not fft_data or rpm_actual <= 0:
        return {
            "available": False,
            "message": "FFT data not available or RPM invalid",
            "findings": []
        }
    
    rpm_hz = rpm_actual / 60.0
    findings = []
    
    # Analisis untuk Driver
    driver_fft = fft_data.get("driver", {})
    for direction in ["H", "V", "A"]:
        freq_key = f"FFT_Freq_{direction}"
        amp_key = f"FFT_Amp_{direction}"
        
        peak_freq = driver_fft.get(freq_key, 0.0)
        peak_amp = driver_fft.get(amp_key, 0.0)
        
        if peak_freq > 0.5 and peak_amp > 0.5:
            ratio = peak_freq / rpm_hz if rpm_hz > 0 else 0
            
            if 0.95 <= ratio <= 1.05:
                fault = "1x RPM - Unbalance (Impeller erosion/fouling)"
                confidence = "HIGH" if peak_amp > 2.0 else "MEDIUM"
            elif 1.95 <= ratio <= 2.05:
                fault = "2x RPM - Misalignment (Coupling/pipe strain)"
                confidence = "HIGH" if peak_amp > 2.0 else "MEDIUM"
            elif 0.35 <= ratio <= 0.45:
                fault = "BPFO - Outer Race Bearing Defect"
                confidence = "MEDIUM"
            elif 0.55 <= ratio <= 0.65:
                fault = "BPFI - Inner Race Bearing Defect"
                confidence = "MEDIUM"
            elif 6.0 <= ratio <= 8.0:
                fault = "Vane Pass Frequency - Hydraulic Instability"
                confidence = "MEDIUM"
            else:
                fault = f"Unknown ({ratio:.1f}x RPM)"
                confidence = "LOW"
            
            findings.append({
                "component": "Driver (Motor)",
                "direction": direction,
                "frequency_hz": round(peak_freq, 1),
                "amplitude_mms": round(peak_amp, 2),
                "ratio_to_rpm": round(ratio, 2),
                "fault": fault,
                "confidence": confidence
            })
    
    # Analisis untuk Driven
    driven_fft = fft_data.get("driven", {})
    for direction in ["H", "V", "A"]:
        freq_key = f"FFT_Freq_{direction}"
        amp_key = f"FFT_Amp_{direction}"
        
        peak_freq = driven_fft.get(freq_key, 0.0)
        peak_amp = driven_fft.get(amp_key, 0.0)
        
        if peak_freq > 0.5 and peak_amp > 0.5:
            ratio = peak_freq / rpm_hz if rpm_hz > 0 else 0
            
            if 0.95 <= ratio <= 1.05:
                fault = "1x RPM - Unbalance (Impeller erosion/fouling)"
                confidence = "HIGH" if peak_amp > 2.0 else "MEDIUM"
            elif 1.95 <= ratio <= 2.05:
                fault = "2x RPM - Misalignment (Coupling/pipe strain)"
                confidence = "HIGH" if peak_amp > 2.0 else "MEDIUM"
            elif 0.35 <= ratio <= 0.45:
                fault = "BPFO - Outer Race Bearing Defect"
                confidence = "MEDIUM"
            elif 0.55 <= ratio <= 0.65:
                fault = "BPFI - Inner Race Bearing Defect"
                confidence = "MEDIUM"
            elif 6.0 <= ratio <= 8.0:
                fault = "Vane Pass Frequency - Hydraulic Instability"
                confidence = "MEDIUM"
            else:
                fault = f"Unknown ({ratio:.1f}x RPM)"
                confidence = "LOW"
            
            findings.append({
                "component": "Driven (Pump)",
                "direction": direction,
                "frequency_hz": round(peak_freq, 1),
                "amplitude_mms": round(peak_amp, 2),
                "ratio_to_rpm": round(ratio, 2),
                "fault": fault,
                "confidence": confidence
            })
    
    return {
        "available": True,
        "rpm_actual": rpm_actual,
        "rpm_hz": round(rpm_hz, 2),
        "findings": findings,
        "count": len(findings),
        "has_issue": len(findings) > 0 and any(f["confidence"] in ["HIGH", "MEDIUM"] for f in findings),
        "standard": "ISO 13373-3 §6.2.2"
    }


def requires_power_off_test(primary_type, electrical_report):
    """
    Determine if power-off test validation is required
    """
    if primary_type != "MECHANICAL":
        return False
    
    voltage_imbalance = electrical_report.get("voltage", {}).get("imbalance_pct", 100.0)
    current_imbalance = electrical_report.get("current", {}).get("imbalance_pct", 100.0)
    load_pct = electrical_report.get("load", {}).get("percentage", 0.0)
    slip_pct = electrical_report.get("slip", {}).get("slip_pct", 100.0)
    
    electrical_ok = (
        voltage_imbalance <= 2.0 and
        current_imbalance <= 5.0 and
        load_pct <= 110.0 and
        slip_pct >= -2.0 and
        slip_pct <= 5.0
    )
    
    return electrical_ok


def prioritize_diagnosis(hydraulic_report, electrical_report, mechanical_report, thermal_report, fft_analysis=None):
    """
    Prioritaskan diagnosa berdasarkan causal hierarchy
    
    API 610 12th Ed. Annex L.3.2:
    "Cavitation generates vibration that may be misinterpreted as mechanical defect. 
     Verify NPSHa and high-frequency vibration BEFORE mechanical intervention."
    """
    issues = {}
    
    if hydraulic_report.get("has_issue", False):
        issues["HYDRAULIC"] = {
            "report": hydraulic_report,
            "priority": DIAGNOSIS_PRIORITY.index("HYDRAULIC"),
            "standard": hydraulic_report.get("standard", "API 610 §6.3.3")
        }
    
    if electrical_report.get("has_issue", False):
        issues["ELECTRICAL"] = {
            "report": electrical_report,
            "priority": DIAGNOSIS_PRIORITY.index("ELECTRICAL"),
            "standard": electrical_report.get("standard", "IEC 60034-1 §4.2")
        }
    
    if fft_analysis and fft_analysis.get("has_issue", False):
        issues["MECHANICAL_FFT"] = {
            "report": fft_analysis,
            "priority": DIAGNOSIS_PRIORITY.index("MECHANICAL"),
            "standard": fft_analysis.get("standard", "ISO 13373-3 §6.2.2")
        }
    
    if mechanical_report.get("has_issue", False):
        issues["MECHANICAL"] = {
            "report": mechanical_report,
            "priority": DIAGNOSIS_PRIORITY.index("MECHANICAL"),
            "standard": mechanical_report.get("standard", "ISO 10816-3")
        }
    
    if thermal_report.get("has_issue", False):
        issues["THERMAL"] = {
            "report": thermal_report,
            "priority": DIAGNOSIS_PRIORITY.index("THERMAL"),
            "standard": "API 610 §11.3"
        }
    
    sorted_issues = sorted(issues.items(), key=lambda x: x[1]["priority"])
    
    if sorted_issues:
        primary_type, primary_data = sorted_issues[0]
        primary_report = primary_data["report"]
        primary_standard = primary_data["standard"]
        
        secondary_note = None
        
        if primary_type == "HYDRAULIC":
            secondary_note = (
                "⚠️ API 610 Annex L.3.2: Mechanical vibration symptoms may be secondary to hydraulic instability. "
                "Fix hydraulic issue first, then re-measure vibration before mechanical intervention."
            )
        elif primary_type == "ELECTRICAL" and mechanical_report.get("has_issue", False):
            if electrical_report.get("slip", {}).get("status") == "ABNORMAL":
                secondary_note = (
                    "⚠️ IEC 60034-1 §4.2: Mechanical vibration symptoms may be secondary to RPM abnormality. "
                    "Verify tachometer calibration, check for backflow (check valve), or grid frequency issue. "
                    "Fix electrical issue first, then re-measure vibration."
                )
            else:
                secondary_note = (
                    "⚠️ IEC 60034-1 §4.2: Mechanical vibration symptoms may be secondary to electrical issue. "
                    "Fix electrical issue first, then re-measure vibration."
                )
        
        if primary_type == "MECHANICAL_FFT":
            primary_type = "MECHANICAL"
        
        primary_diagnosis = {
            "type": primary_type,
            "report": primary_report,
            "secondary_note": secondary_note,
            "standard": primary_standard
        }
        
        requires_validation = requires_power_off_test(primary_type, electrical_report)
    else:
        primary_diagnosis = {
            "type": "NORMAL",
            "report": {"status": "All parameters within normal limits"},
            "secondary_note": None,
            "standard": "ISO 10816-3 Zone A"
        }
        requires_validation = False
    
    return {
        "primary_diagnosis": primary_diagnosis,
        "requires_power_off_test": requires_validation,
        "all_issues": sorted_issues,
        "issue_count": len(sorted_issues),
        "has_issues": len(sorted_issues) > 0
    }


def calculate_age_risk_factor(installation_year, current_year=2026):
    """Hitung age-based risk factor (ISO 55001:2014 §8.2)"""
    age = current_year - installation_year
    if age > 15:
        return 1.5
    elif age > 10:
        return 1.2
    else:
        return 1.0


def generate_action_plan(diagnosis_result, spec_data, metadata):
    """Generate action plan berdasarkan diagnosis"""
    primary = diagnosis_result["primary_diagnosis"]
    primary_type = primary["type"]
    
    product_type = spec_data.get("product_type", "Diesel")
    pump_size = spec_data.get("pump_size", "Medium")
    installation_year = spec_data.get("installation_year", 2018)
    pump_tag = metadata.get("pump_tag", "Unknown")
    
    product_risk_factor = {
        "Gasoline": 5,
        "Avtur": 4,
        "Naphtha": 5,
        "Diesel": 3
    }.get(product_type, 3)
    
    age_risk_factor = calculate_age_risk_factor(installation_year)
    
    if primary_type == "NORMAL":
        risk_score = 0
        risk_level = "LOW"
        actions = [{
            "priority": "ROUTINE",
            "action": "Continue routine monitoring",
            "timeline": "Next scheduled inspection",
            "pic": "Maintenance Team",
            "standard": "ISO 55001 §8.2"
        }]
    
    elif primary_type == "HYDRAULIC":
        report = primary["report"]
        
        if report["cavitation_risk"] == "HIGH":
            base_risk = product_risk_factor * 5
            risk_score = min(int(base_risk * age_risk_factor), 100)
            risk_level = "CRITICAL"
            
            actions = [
                {
                    "priority": "CRITICAL",
                    "action": f"⚠️ VOLATILE PRODUCT ({product_type}): Monitor seal temperature continuously - risk of seal failure",
                    "timeline": "Continuous",
                    "pic": "Operations Team",
                    "standard": "API 682 §5.4.2"
                },
                {
                    "priority": "IMMEDIATE",
                    "action": f"Increase suction pressure or tank level to achieve NPSHa > {report['npshr'] + 1.0} m",
                    "timeline": "< 4 hours" if product_type in ["Gasoline", "Avtur"] else "< 24 hours",
                    "pic": "Operations Team",
                    "standard": "API 610 §6.3.3"
                },
                {
                    "priority": "HIGH",
                    "action": "⚠️ MANDATORY RE-MEASURE: Re-measure vibration after hydraulic correction before mechanical intervention",
                    "timeline": "24-48 hours",
                    "pic": "Vibration Analyst",
                    "standard": "API 610 Annex L.3.2"
                }
            ]
        
        elif report["flow_status"] != "NORMAL":
            base_risk = product_risk_factor * 3
            risk_score = min(int(base_risk * age_risk_factor), 100)
            risk_level = "HIGH"
            
            actions = [
                {
                    "priority": "HIGH",
                    "action": f"Adjust flow to 60-120% BEP ({0.6 * report['bep_flow']:.0f} - {1.2 * report['bep_flow']:.0f} m³/h)",
                    "timeline": "< 24 hours",
                    "pic": "Operations Team",
                    "standard": "API 610 Annex L"
                },
                {
                    "priority": "MEDIUM",
                    "action": "⚠️ MANDATORY RE-MEASURE: Re-measure vibration after flow adjustment",
                    "timeline": "< 7 days",
                    "pic": "Vibration Analyst",
                    "standard": "API 610 Annex L.3.2"
                }
            ]
        
        else:
            base_risk = product_risk_factor * 2
            risk_score = min(int(base_risk * age_risk_factor), 100)
            risk_level = "MEDIUM"
            actions = []
    
    elif primary_type == "ELECTRICAL":
        report = primary["report"]
        
        if report["overall_status"] == "CRITICAL":
            base_risk = product_risk_factor * 4
            risk_score = min(int(base_risk * age_risk_factor), 100)
            risk_level = "CRITICAL"
            
            actions = [
                {
                    "priority": "IMMEDIATE",
                    "action": "Shut down motor - electrical imbalance or overload detected",
                    "timeline": "< 2 hours",
                    "pic": "Electrical Team",
                    "standard": "IEC 60034-1 §4.2"
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
            base_risk = product_risk_factor * 3
            risk_score = min(int(base_risk * age_risk_factor), 100)
            risk_level = "HIGH"
            
            actions = [
                {
                    "priority": "HIGH",
                    "action": "Investigate voltage/current imbalance or slip abnormality",
                    "timeline": "< 72 hours",
                    "pic": "Electrical Team",
                    "standard": "IEC 60034-1 §4.2"
                },
                {
                    "priority": "MEDIUM",
                    "action": "⚠️ MANDATORY RE-MEASURE: Re-measure vibration after electrical correction",
                    "timeline": "< 7 days",
                    "pic": "Vibration Analyst",
                    "standard": "IEC 60034-1 §4.2"
                }
            ]
        
        else:
            base_risk = product_risk_factor * 2
            risk_score = min(int(base_risk * age_risk_factor), 100)
            risk_level = "MEDIUM"
            actions = []
    
    elif primary_type == "MECHANICAL":
        report = primary["report"]
        
        actions = []
        if diagnosis_result.get("requires_power_off_test", False):
            actions.append({
                "priority": "MEDIUM",
                "action": "⚠️ POWER-OFF TEST REQUIRED: Differentiate electrical vs mechanical unbalance",
                "timeline": "Before mechanical repair",
                "pic": "Vibration Analyst",
                "standard": "API 610 Annex L.3.2",
                "validation_procedure": (
                    "1. Measure vibration while motor running\n"
                    "2. Shut down motor safely\n"
                    "3. Measure vibration during coast-down (2-3 min)\n"
                    "4. Interpret:\n"
                    "   • Gradual decay with RPM → MECHANICAL unbalance\n"
                    "   • Immediate drop to <1.0 mm/s → ELECTRICAL unbalance\n"
                    "   • Persists after shutdown → bearing defect/looseness"
                )
            })
        
        if "findings" in report:
            base_risk = product_risk_factor * 3
            risk_score = min(int(base_risk * age_risk_factor), 100)
            risk_level = "HIGH"
            
            for finding in report["findings"]:
                if finding["confidence"] in ["HIGH", "MEDIUM"]:
                    actions.append({
                        "priority": "HIGH" if finding["confidence"] == "HIGH" else "MEDIUM",
                        "action": f"FFT Peak {finding['frequency_hz']} Hz ({finding['ratio_to_rpm']}x RPM): {finding['fault']}",
                        "timeline": "< 7 days" if finding["confidence"] == "HIGH" else "< 14 days",
                        "pic": "Vibration Analyst",
                        "standard": "ISO 13373-3 §6.2.2"
                    })
        else:
            if report["overall_zone"] == "D":
                base_risk = product_risk_factor * 4
                risk_score = min(int(base_risk * age_risk_factor), 100)
                risk_level = "CRITICAL"
                
                actions.extend([
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
                ])
            
            elif report["overall_zone"] == "C":
                base_risk = product_risk_factor * 3
                risk_score = min(int(base_risk * age_risk_factor), 100)
                risk_level = "HIGH"
                
                actions.append({
                    "priority": "HIGH",
                    "action": f"Schedule {report['primary_fault'].lower()} correction",
                    "timeline": "< 14 days",
                    "pic": "Maintenance Team",
                    "standard": "ISO 10816-3 Zone C"
                })
            
            else:
                base_risk = product_risk_factor * 2
                risk_score = min(int(base_risk * age_risk_factor), 100)
                risk_level = "MEDIUM"
    
    elif primary_type == "THERMAL":
        report = primary["report"]
        
        if report["overall_status"] == "CRITICAL":
            base_risk = product_risk_factor * 4
            risk_score = min(int(base_risk * age_risk_factor), 100)
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
            base_risk = product_risk_factor * 3
            risk_score = min(int(base_risk * age_risk_factor), 100)
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
            base_risk = product_risk_factor * 2
            risk_score = min(int(base_risk * age_risk_factor), 100)
            risk_level = "MEDIUM"
            actions = []
    
    else:
        risk_score = 0
        risk_level = "UNKNOWN"
        actions = []
    
    if risk_score > 0 and not actions:
        actions = [{
            "priority": "ROUTINE",
            "action": "Update asset register & schedule follow-up inspection",
            "timeline": "After completion",
            "pic": "Reliability Engineer",
            "standard": "ISO 55001 §8.2"
        }]
    elif risk_score > 0:
        if actions[-1].get("priority") != "ROUTINE":
            actions.append({
                "priority": "ROUTINE",
                "action": "Update asset register & schedule follow-up inspection",
                "timeline": "After completion",
                "pic": "Reliability Engineer",
                "standard": "ISO 55001 §8.2"
            })
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "actions": actions,
        "primary_issue": primary_type,
        "pump_tag": pump_tag,
        "product_type": product_type,
        "installation_year": installation_year,
        "age_risk_factor": age_risk_factor
    }


def run_complete_diagnosis(input_data):
    """Jalankan diagnosa lengkap - causal hierarchy intact"""
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
    
    actual_rpm = input_data.get("rpm", None)
    fft_data = input_data.get("fft", {})
    
    hf_driver = vibration_data["driver"].get("HF_5_16kHz", 0.0)
    hf_driven = vibration_data["driven"].get("HF_5_16kHz", 0.0)
    
    hydraulic_report = generate_hydraulic_report(
        operational_data,
        spec_data,
        hf_5_16khz_driver=hf_driver,
        hf_5_16khz_driven=hf_driven
    )
    
    electrical_report = generate_electrical_report(
        electrical_data,
        spec_data,
        actual_rpm=actual_rpm
    )
    
    thermal_report = generate_thermal_report(thermal_data)
    
    mechanical_report = analyze_mechanical_conditions(
        vibration_data["driver"],
        vibration_data["driven"],
        spec_data["foundation_type"],
        spec_data["product_type"]
    )
    
    fft_analysis = analyze_fft_peaks(
        fft_data=fft_data,
        rpm_actual=actual_rpm if actual_rpm else 2950,
        spec_data=spec_data
    )
    
    diagnosis_result = prioritize_diagnosis(
        hydraulic_report,
        electrical_report,
        mechanical_report,
        thermal_report,
        fft_analysis=fft_analysis
    )
    
    action_plan = generate_action_plan(diagnosis_result, spec_data, metadata)
    
    return {
        "metadata": metadata,
        "specification": spec_data,
        "analyses": {
            "hydraulic": hydraulic_report,
            "electrical": electrical_report,
            "thermal": thermal_report,
            "mechanical": mechanical_report,
            "fft": fft_analysis
        },
        "diagnosis": diagnosis_result,
        "action_plan": action_plan,
        "summary": generate_summary(diagnosis_result, action_plan)
    }


def generate_summary(diagnosis_result, action_plan):
    """Generate executive summary - Compliance statement tetap di Excel, BUKAN di dashboard"""
    primary = diagnosis_result["primary_diagnosis"]
    primary_type = primary["type"]
    
    if primary_type == "NORMAL":
        summary_text = "✅ **All systems normal** - Continue routine monitoring (ISO 10816-3 Zone A)"
        color = "green"
    elif primary_type == "HYDRAULIC":
        summary_text = f"🚨 **PRIMARY ISSUE: Hydraulic** - {primary['report'].get('cavitation_status', 'Hydraulic issue detected')}<br>**Standard:** {primary['standard']}"
        color = "red" if primary['report'].get('cavitation_risk') == 'HIGH' else "orange"
    elif primary_type == "ELECTRICAL":
        summary_text = f"⚡ **PRIMARY ISSUE: Electrical** - {primary['report']['overall_status']} condition detected<br>**Standard:** {primary['standard']}"
        color = "red" if primary['report']['overall_status'] == 'CRITICAL' else "orange"
    elif primary_type == "MECHANICAL":
        power_off_note = ""
        if diagnosis_result.get("requires_power_off_test", False):
            power_off_note = "<br>⚠️ <span style='color:orange'>POWER-OFF TEST REQUIRED before mechanical repair</span>"
        
        if "findings" in primary['report']:
            summary_text = f"🔧 **PRIMARY ISSUE: Mechanical (FFT)** - {len(primary['report']['findings'])} significant peaks detected<br>**Standard:** {primary['standard']}{power_off_note}"
            color = "orange"
        else:
            summary_text = f"🔧 **PRIMARY ISSUE: Mechanical** - Zone {primary['report']['overall_zone']} vibration, {primary['report']['primary_fault']}<br>**Standard:** {primary['standard']}{power_off_note}"
            color = "red" if primary['report']['overall_zone'] == 'D' else "orange"
    elif primary_type == "THERMAL":
        summary_text = f"🌡️ **PRIMARY ISSUE: Thermal** - Bearing temperature {primary['report']['overall_status']}<br>**Standard:** API 610 §11.3"
        color = "red" if primary['report']['overall_status'] == 'CRITICAL' else "orange"
    else:
        summary_text = "❓ **Unknown status**"
        color = "gray"
    
    # NOTE: Compliance statement string tetap di-generate untuk Excel report
    # TAPI TIDAK DITAMPILKAN di dashboard (dihapus di report_generator.py)
    return {
        "summary_text": summary_text,
        "color": color,
        "risk_level": action_plan["risk_level"],
        "risk_score": action_plan["risk_score"],
        "action_count": len(action_plan["actions"]),
        "compliance_statement": (
            "This diagnosis complies with:<br>"
            "• API 610 12th Ed. §6.3.3 (Cavitation detection via HF vibration)<br>"
            "• API 610 Annex L.3.2 (Causal hierarchy: hydraulic before mechanical)<br>"
            "• ISO 13373-1:2012 §5.3.2 (Vibration as symptom, not root cause)<br>"
            "• IEC 60034-1:2017 §4.2 (Slip monitoring for overload detection)<br>"
            "• ISO 15243:2017 §5.2 (Demodulation for bearing defect detection)<br>"
            "• ISO 55001:2014 §8.2 (Age-based risk adjustment)"
        )
    }
