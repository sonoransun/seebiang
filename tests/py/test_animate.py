from seebiang.io import Stroke
from seebiang.animate import progresses_at_time, total_duration_ms, frame_count


def _strokes(*durations):
    return tuple(Stroke(index=i, path="M 0 0 L 1 1", duration_ms=d) for i, d in enumerate(durations))


def test_total_duration():
    s = _strokes(100, 200, 300)
    assert total_duration_ms(s) == 600


def test_progress_at_zero_is_all_zero():
    s = _strokes(100, 200)
    assert progresses_at_time(0, s) == [0.0, 0.0]


def test_progress_at_end_is_all_one():
    s = _strokes(100, 200)
    assert progresses_at_time(300, s) == [1.0, 1.0]


def test_progress_midway_through_second_stroke():
    s = _strokes(100, 200)
    # 100ms in → first stroke complete, second at 0
    assert progresses_at_time(100, s) == [1.0, 0.0]
    # 200ms in → second stroke half-drawn
    assert progresses_at_time(200, s) == [1.0, 0.5]


def test_frame_count_scales_with_fps():
    s = _strokes(1000)
    assert frame_count(30, s, tail_ms=0) == 30
    assert frame_count(60, s, tail_ms=0) == 60
