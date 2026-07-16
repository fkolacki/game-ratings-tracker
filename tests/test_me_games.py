from conftest import fake_fetch_games_multiple

def test_add_game_to_list(client, auth_headers, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    test_add = client.post("/me/games/1/", json={"status": "playing", "user_rating": 4.4}, headers=auth_headers)
    assert test_add.status_code == 200
    assert "playing" == test_add.json()["status"]

def test_add_game_does_not_exist(client, auth_headers, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    test_add = client.post("/me/games/1999/", json={"status": "playing", "user_rating": 4.4}, headers=auth_headers)
    assert test_add.status_code == 404

def test_update_game(client, auth_headers, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    test_add = client.post("/me/games/1/", json={"status": "playing", "user_rating": 4.4}, headers=auth_headers)
    test_update = client.patch("/me/games/1/", json={"status": "completed", "user_rating": 5}, headers=auth_headers)
    assert test_update.status_code == 200
    assert "completed" == test_update.json()["status"]

def test_me_games(client, auth_headers, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    client.post("/me/games/1/", json={"status": "playing", "user_rating": 4.4}, headers=auth_headers)
    test_my_games = client.get("/me/games/", headers=auth_headers)
    assert test_my_games.status_code == 200
    assert len(test_my_games.json()) == 1
    assert "playing" == test_my_games.json()[0]["status"]

def test_me_stats(client, auth_headers, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    client.post("/me/games/1/", json={"status": "playing", "user_rating": 4.4}, headers=auth_headers)
    client.post("/me/games/2/", json={"status": "completed", "user_rating": 4.7}, headers=auth_headers)
    test_my_stats = client.get("/me/stats/", headers=auth_headers)
    assert test_my_stats.status_code == 200
    assert 2 == test_my_stats.json()["total_games"]
    assert 4.55 == round(test_my_stats.json()["user_rating_avg"], 2)