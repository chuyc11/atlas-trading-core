from trading_core.data.point_in_time import is_available, normalize_pit_record


def test_point_in_time_availability() -> None:
    strong = {
        "event_time": "2026-06-23 15:00:00",
        "publish_time": "2026-06-23 15:05:00",
        "available_time": "2026-06-23 15:10:00",
        "as_of_time": "2026-06-23 15:10:00",
    }
    assert is_available(strong, "2026-06-23 15:11:00")
    assert not is_available(strong, "2026-06-23 15:09:00")
    assert normalize_pit_record({"date": "2026-06-23"})["pit_quality"] == "weak"
