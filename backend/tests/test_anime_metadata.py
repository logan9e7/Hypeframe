from app.anime_metadata import search_jikan_anime
import pytest

def test_reject_empty_title():
    with pytest.raises(ValueError):
        search_jikan_anime('')
