from app import providers
import pytest

def test_invalid_title():
    with pytest.raises(ValueError):
        providers.search_metadata('')

def test_unknown_provider():
    with pytest.raises(ValueError):
        providers.search_metadata('Naruto', provider='random')

def test_combines_all_providers(monkeypatch):
    monkeypatch.setattr(providers, '_CACHE', {})
    for name in ('jikan', 'anilist', 'kitsu'):
        monkeypatch.setitem(providers._PROVIDERS, name, lambda q, n, name=name: [{'source': name, 'title': q}])
    result = providers.search_metadata('Naruto')
    assert {r['source'] for r in result['results']} == {'jikan', 'anilist', 'kitsu'}
    assert result['unavailable_providers'] == []

def test_independent_failure(monkeypatch):
    monkeypatch.setattr(providers, '_CACHE', {})
    def broken(q, n):
        raise OSError('provider offline')
    monkeypatch.setitem(providers._PROVIDERS, 'jikan', broken)
    monkeypatch.setitem(providers._PROVIDERS, 'kitsu', lambda q, n: [{'source': 'kitsu'}])
    result = providers.search_metadata('Bleach', 'all')
    assert 'jikan' in result['unavailable_providers']
    assert any(x['source'] == 'kitsu' for x in result['results'])
