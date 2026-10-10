"""
PairCover-Q — Historical EMS Dataset Validation & Provenance Module.

Audits, parses and validates candidate emergency dispatch CSV files (such as
the TNHSP 108 schema or municipal EMS records), reporting column availability,
data integrity, and empirical response time statistics without conflating historical
observations with real-time all-pairs optimizer inputs.
"""

from __future__ import annotations

import csv
import io
import math
from typing import Any, Mapping, Sequence


# Recognized column aliases based on official TNHSP 108 documentation & standard EMS schemas
FIELD_ALIASES = {
    "case_id": ["case_id", "case id", "incident_id", "call_id", "id"],
    "call_time": ["call date", "call_date", "calldate", "call_time", "call time", "timestamp", "date"],
    "case_type": ["emergency type", "emergency_type", "em sub type", "case_type", "incident_type", "call_type"],
    "ambulance_type": ["vehicle type", "vehicle_type", "ambulance_type", "als_bls", "unit_type"],
    "location": ["caller taluk", "caller_taluk", "caller district", "caller_district", "district", "taluk", "area", "zone"],
    "assignment_time": ["case assigned time", "case_assigned_time", "assigned_time", "dispatch_time"],
    "scene_arrival_time": ["scene arrival time", "scene_arrival_time", "arrival_time", "reach_time"],
    "response_time": ["response time", "response_time", "rt", "duration_min", "response_minutes"],
    "distance": ["bs(km)", "bs_km", "distance", "distance_km", "b2b(km)", "km"],
}


def detect_field_mapping(header: Sequence[str]) -> dict[str, str | None]:
    """Maps canonical field concepts to actual CSV column names present in header."""
    norm_header = {h.strip().lower(): h for h in header}
    mapping: dict[str, str | None] = {}
    for canonical, aliases in FIELD_ALIASES.items():
        matched = None
        for alias in aliases:
            if alias in norm_header:
                matched = norm_header[alias]
                break
        mapping[canonical] = matched
    return mapping


def _safe_float(val: Any) -> float | None:
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("na", "nan", "null", "none", "—", "-"):
        return None
    try:
        f = float(s)
        return f if not math.isnan(f) else None
    except ValueError:
        return None


def validate_ems_csv(
    file_or_path: Any,
    delimiter: str = ","
) -> dict[str, Any]:
    """
    Validates an uploaded or local EMS CSV file, returning schema audit,
    data health metrics, and empirical summary statistics.
    """
    if isinstance(file_or_path, str):
        if not file_or_path.strip():
            content = ""
        elif "\n" in file_or_path or "," in file_or_path:
            content = file_or_path
        else:
            try:
                with open(file_or_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except (FileNotFoundError, OSError):
                content = file_or_path
    elif hasattr(file_or_path, "read"):
        raw = file_or_path.read()
        content = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
    elif isinstance(file_or_path, bytes):
        content = file_or_path.decode("utf-8", errors="replace")
    else:
        content = str(file_or_path)

    lines = content.splitlines()
    if not lines or not any(line.strip() for line in lines):
        return {
            "is_valid": False,
            "row_count": 0,
            "columns": [],
            "detected_fields": {},
            "missing_critical_fields": list(FIELD_ALIASES.keys()),
            "errors": ["File is empty or contains only whitespace."],
            "warnings": [],
            "stats": {},
            "provenance_disclosure": (
                "No data could be read. Scenarios in PairCover-Q remain strictly synthetic."
            )
        }

    reader = csv.reader(lines, delimiter=delimiter)
    header = next(reader, None)
    if not header:
        return {
            "is_valid": False,
            "row_count": 0,
            "columns": [],
            "detected_fields": {},
            "missing_critical_fields": list(FIELD_ALIASES.keys()),
            "errors": ["No CSV header row detected."],
            "warnings": [],
            "stats": {},
            "provenance_disclosure": (
                "Missing header. Scenarios in PairCover-Q remain strictly synthetic."
            )
        }

    clean_header = [h.strip() for h in header]
    field_map = detect_field_mapping(clean_header)
    
    rows = list(reader)
    total_rows = len(rows)

    errors = []
    warnings = []
    
    if total_rows == 0:
        errors.append("CSV contains a header but zero data rows.")

    # Check which expected concepts are missing
    critical_concepts = ["call_time", "response_time", "location"]
    missing_critical = [c for c in critical_concepts if field_map.get(c) is None]
    if missing_critical:
        warnings.append(
            f"Missing common EMS fields: {', '.join(missing_critical)}. "
            "Data may lack required context for response time distribution modeling."
        )

    # Column index lookups
    col_idx = {h: i for i, h in enumerate(clean_header)}
    rt_col = field_map.get("response_time")
    dist_col = field_map.get("distance")
    case_col = field_map.get("case_type")
    amb_col = field_map.get("ambulance_type")

    response_times: list[float] = []
    distances: list[float] = []
    case_types: dict[str, int] = {}
    amb_types: dict[str, int] = {}
    
    missing_counts: dict[str, int] = {col: 0 for col in clean_header}
    invalid_numbers_count = 0

    for r_idx, r in enumerate(rows, 1):
        # Count missing cells
        for col_name, c_i in col_idx.items():
            val = r[c_i] if c_i < len(r) else ""
            if not val.strip():
                missing_counts[col_name] += 1

        # Response time extraction
        if rt_col and col_idx.get(rt_col) is not None:
            c_i = col_idx[rt_col]
            if c_i < len(r):
                val_f = _safe_float(r[c_i])
                if val_f is not None:
                    if val_f < 0:
                        invalid_numbers_count += 1
                    else:
                        response_times.append(val_f)

        # Distance extraction
        if dist_col and col_idx.get(dist_col) is not None:
            c_i = col_idx[dist_col]
            if c_i < len(r):
                val_f = _safe_float(r[c_i])
                if val_f is not None:
                    if val_f < 0:
                        invalid_numbers_count += 1
                    else:
                        distances.append(val_f)

        # Categoricals
        if case_col and col_idx.get(case_col) is not None:
            c_i = col_idx[case_col]
            if c_i < len(r) and r[c_i].strip():
                k = r[c_i].strip()
                case_types[k] = case_types.get(k, 0) + 1

        if amb_col and col_idx.get(amb_col) is not None:
            c_i = col_idx[amb_col]
            if c_i < len(r) and r[c_i].strip():
                k = r[c_i].strip()
                amb_types[k] = amb_types.get(k, 0) + 1

    if invalid_numbers_count > 0:
        warnings.append(f"Found {invalid_numbers_count} rows with negative duration or distance values.")

    # Calculate statistics
    stats: dict[str, Any] = {
        "total_records": total_rows,
        "valid_records_analyzed": len(rows),
        "column_missing_rates": {
            col: round(cnt / total_rows, 4) if total_rows else 0.0
            for col, cnt in missing_counts.items()
        }
    }

    if response_times:
        s_rt = sorted(response_times)
        n = len(s_rt)
        mean_rt = sum(s_rt) / n
        median_rt = s_rt[n // 2] if n % 2 != 0 else (s_rt[n // 2 - 1] + s_rt[n // 2]) / 2.0
        p90_idx = int(math.ceil(0.9 * n)) - 1
        p90_rt = s_rt[max(0, min(p90_idx, n - 1))]
        stats["response_time"] = {
            "count": n,
            "min": round(s_rt[0], 2),
            "median": round(median_rt, 2),
            "mean": round(mean_rt, 2),
            "p90": round(p90_rt, 2),
            "max": round(s_rt[-1], 2),
        }

    if distances:
        s_dist = sorted(distances)
        n = len(s_dist)
        mean_d = sum(s_dist) / n
        median_d = s_dist[n // 2] if n % 2 != 0 else (s_dist[n // 2 - 1] + s_dist[n // 2]) / 2.0
        stats["distance"] = {
            "count": n,
            "min": round(s_dist[0], 2),
            "median": round(median_d, 2),
            "mean": round(mean_d, 2),
            "max": round(s_dist[-1], 2),
        }

    if case_types:
        stats["case_types_top"] = sorted(case_types.items(), key=lambda x: x[1], reverse=True)[:5]

    if amb_types:
        stats["ambulance_types"] = dict(sorted(amb_types.items(), key=lambda x: x[1], reverse=True))

    is_valid = len(errors) == 0 and total_rows > 0

    return {
        "is_valid": is_valid,
        "row_count": total_rows,
        "columns": clean_header,
        "detected_fields": {k: v for k, v in field_map.items() if v is not None},
        "missing_fields": [k for k, v in field_map.items() if v is None],
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
        "provenance_disclosure": (
            "HISTORICAL RECORD BOUNDARY: These historical records provide empirical duration distributions "
            "for past calls, but do NOT contain candidate travel times from every idle unit to new calls. "
            "They cannot be silently fed into real-time dispatch optimization without external travel-time matrix estimation."
        )
    }
