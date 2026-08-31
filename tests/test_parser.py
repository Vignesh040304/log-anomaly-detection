from src.parser import normalize_message, parse_line, parse_logs

def test_normalize_masks_volatile_values():
    msg = "Login failed user_id=123 ip=10.1.2.3 request=550e8400-e29b-41d4-a716-446655440000"
    normalized = normalize_message(msg)
    assert "<ip>" in normalized
    assert "<num>" in normalized
    assert "<uuid>" in normalized

def test_parse_generic_line():
    row = parse_line("2026-08-31 10:00:00 ERROR auth Login failed status=401 response_ms=900")
    assert row["level"] == "ERROR"
    assert row["service"] == "auth"
    assert row["status_code"] == 401
    assert row["response_ms"] == 900

def test_parse_logs_keeps_rows():
    text = "\n".join(
        f"2026-08-31 10:00:{i:02d} INFO api Request completed status=200 response_ms=20"
        for i in range(10)
    )
    frame = parse_logs(text)
    assert len(frame) == 10
    assert "normalized_message" in frame.columns
