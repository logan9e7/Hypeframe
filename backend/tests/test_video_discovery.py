from app.video_discovery import parse_youtube_id

def test_watch_url():
    assert parse_youtube_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'

def test_short_url():
    assert parse_youtube_id('https://youtu.be/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'

def test_reject_lookalike_domain():
    assert parse_youtube_id('https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ') is None

def test_reject_non_video_url():
    assert parse_youtube_id('https://www.youtube.com/@channel') is None
