from conftest import fake_fetch_games_multiple

def test_pagination_limit(client, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    test_get_game1 = client.get("/games/", params={"limit": 1})
    assert "test_game" == test_get_game1.json()[0]["title"]
    assert len(test_get_game1.json()) == 1
    test_get_game2 = client.get("/games/", params={"skip": 1, "limit": 1})
    assert len(test_get_game2.json()) == 1
    assert "test_game2" == test_get_game2.json()[0]["title"]

def test_pagination_limit_me(client, auth_headers, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    client.post("/me/games/1/", json={"status": "playing", "user_rating": 4.4}, headers=auth_headers)
    client.post("/me/games/2/", json={"status": "completed", "user_rating": 4.7}, headers=auth_headers)
    test_my_game1 = client.get("/me/games/", params={"limit":1}, headers=auth_headers)
    assert len(test_my_game1.json()) == 1
    assert "playing" == test_my_game1.json()[0]["status"]
    test_my_game2 = client.get("/me/games/", params={"skip": 1, "limit": 1}, headers=auth_headers)
    assert len(test_my_game2.json()) == 1
    assert "completed" == test_my_game2.json()[0]["status"]