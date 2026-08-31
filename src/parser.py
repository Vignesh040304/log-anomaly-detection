"""Parsing and normalization utilities for semi-structured logs."""
from __future__ import annotations
import re
from typing import Any
import pandas as pd

GENERIC_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d{3})?)\s+"
    r"(?P<level>[A-Za-z]+)\s+(?P<service>[\w.-]+)\s+(?P<message>.*)$"
)
APACHE_RE = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)(?:\s+HTTP/\d\.\d)?"\s+'
    r"(?P<status>\d{3})\s+(?P<size>\d+)(?:\s+(?P<rest>.*))?$"
)

def normalize_message(message: str) -> str:
    value = message.lower()
    value = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", "<uuid>", value)
    value = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", value)
    value = re.sub(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", "<email>", value)
    value = re.sub(r"\b(?:0x)?[0-9a-f]{12,}\b", "<hex>", value)
    value = re.sub(r"\b\d+\b", "<num>", value)
    return re.sub(r"\s+", " ", value).strip()

def _metadata(message: str) -> dict[str, Any]:
    return {k.lower(): v for k, v in re.findall(r"(\w+)=([^\s]+)", message)}

def _number(value: Any) -> float:
    try:
        return float(re.sub(r"[^\d.]", "", str(value)))
    except (TypeError, ValueError):
        return 0.0

def parse_line(line: str, line_number: int = 1) -> dict[str, Any]:
    raw = line.strip()
    if not raw:
        return {}
    match = GENERIC_RE.match(raw)
    if match:
        data = match.groupdict()
        msg = data["message"]
        meta = _metadata(msg)
        status = meta.get("status", "0")
        return {
            "line_number": line_number,
            "timestamp": pd.to_datetime(data["timestamp"], errors="coerce"),
            "level": data["level"].upper(),
            "service": data["service"],
            "message": msg,
            "normalized_message": normalize_message(msg),
            "status_code": int(status) if str(status).isdigit() else 0,
            "response_ms": _number(meta.get("response_ms", meta.get("latency_ms", 0))),
            "raw": raw,
        }
    match = APACHE_RE.match(raw)
    if match:
        data = match.groupdict()
        status = int(data["status"])
        msg = f'{data["method"]} {data["path"]} status={status} bytes={data["size"]}'
        return {
            "line_number": line_number,
            "timestamp": pd.to_datetime(data["timestamp"], errors="coerce"),
            "level": "ERROR" if status >= 500 else ("WARN" if status >= 400 else "INFO"),
            "service": "web",
            "message": msg,
            "normalized_message": normalize_message(msg),
            "status_code": status,
            "response_ms": 0.0,
            "raw": raw,
        }
    return {
        "line_number": line_number, "timestamp": pd.NaT, "level": "UNKNOWN",
        "service": "unknown", "message": raw,
        "normalized_message": normalize_message(raw), "status_code": 0,
        "response_ms": 0.0, "raw": raw,
    }

def parse_logs(text: str) -> pd.DataFrame:
    rows = [parse_line(line, i) for i, line in enumerate(text.splitlines(), 1)]
    rows = [row for row in rows if row]
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["message_length"] = frame["message"].str.len()
    frame["has_error_keyword"] = frame["message"].str.contains(
        r"error|failed|timeout|exception|denied|refused",
        case=False, regex=True
    ).astype(int)
    return frame
