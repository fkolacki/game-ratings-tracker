from conftest import fake_fetch_games_multiple

def test_sync_creates_new_games(client, mock_rawg_response):
    test_sync = client.post("/games/sync")
    assert test_sync.status_code == 200
    test_game = client.get("/games/")
    assert test_game.status_code == 200
    assert "test_game" == test_game.json()[0]["title"]

def test_sync_does_not_duplicate_existing_game(client, mock_rawg_response, monkeypatch):
    test_sync = client.post("/games/sync")
    def fake_fetch_games_updated():
        test_game = {"id": 1, "name": "test_game_updated",  "genres": [{"name": "Action"}, {"name": "RPG"}], "released": "2024-04-04", "rating": 4.5}
        test_data = {"results": [test_game]}
        return test_data
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_updated)
    client.post("/games/sync")
    test_game = client.get("/games/")
    assert test_game.status_code == 200
    assert len(test_game.json()) == 1
    assert "test_game_updated" == test_game.json()[0]["title"]

def test_filtering_by_genre(client, mock_rawg_response, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    test_game = client.get("/games/", params={"genre": "Sports"})
    assert len(test_game.json()) == 1
    assert "Sports" in test_game.json()[0]["genre"]

def test_filtering_by_min_rating(client, mock_rawg_response, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    test_game = client.get("/games/", params={"min_rating": 4.45})
    assert len(test_game.json()) == 1
    assert test_game.json()[0]["rawg_rating"] == 4.5

def test_filtering_by_year(client, mock_rawg_response, monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games_multiple)
    client.post("/games/sync")
    test_game = client.get("/games/", params={"year": "2025"})
    assert len(test_game.json()) == 1
    assert "2025" in test_game.json()[0]["release_date"]