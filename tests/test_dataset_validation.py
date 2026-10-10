"""
Tests for EMS dataset validation, schema detection and provenance boundaries.
"""

import io
from qrescue.data.validator import validate_ems_csv, detect_field_mapping


def test_detect_field_mapping():
    header = ["Case_ID", "Call Date", "Caller Taluk", "Response Time", "BS(KM)", "Emergency Type", "Vehicle Type"]
    mapping = detect_field_mapping(header)
    assert mapping["case_id"] == "Case_ID"
    assert mapping["call_time"] == "Call Date"
    assert mapping["location"] == "Caller Taluk"
    assert mapping["response_time"] == "Response Time"
    assert mapping["distance"] == "BS(KM)"
    assert mapping["case_type"] == "Emergency Type"
    assert mapping["ambulance_type"] == "Vehicle Type"


def test_validate_ems_csv_valid_content():
    csv_text = """Case_ID,Call Date,Caller Taluk,Emergency Type,Vehicle Type,Response Time,BS(KM)
1001,01/10/2026,Ambattur,Cardiac,ALS,12.5,4.2
1002,01/10/2026,Guindy,Trauma,BLS,8.0,2.1
1003,01/10/2026,Tambaram,Pregnancy,BLS,15.0,6.5
1004,01/10/2026,Saidapet,Cardiac,ALS,10.0,3.0
"""
    report = validate_ems_csv(io.StringIO(csv_text))
    assert report["is_valid"] is True
    assert report["row_count"] == 4
    assert "response_time" in report["stats"]
    rt = report["stats"]["response_time"]
    assert rt["count"] == 4
    assert rt["min"] == 8.0
    assert rt["max"] == 15.0
    assert rt["median"] == 11.25
    assert "HISTORICAL RECORD BOUNDARY" in report["provenance_disclosure"]


def test_validate_ems_csv_empty_and_malformed():
    report_empty = validate_ems_csv("")
    assert report_empty["is_valid"] is False
    assert len(report_empty["errors"]) > 0

    csv_negative = """Incident_ID,Response Time,Distance
A1,-5.0,10.0
A2,12.0,-2.0
"""
    report_neg = validate_ems_csv(io.StringIO(csv_negative))
    assert report_neg["is_valid"] is True
    assert any("negative duration" in w for w in report_neg["warnings"])
