def test_register(client):
    register = client.post("/register/", json={"email": "a@a.com", "password": "password1"})
    assert register.status_code == 200

def test_register_duplicate_email(client):
    first_register = client.post("/register/", json={"email": "a@a.com", "password": "password1"})
    second_register = client.post("/register/", json={"email": "a@a.com", "password": "password1"})
    assert second_register.status_code == 400

def test_login(client):
    user_register = client.post("/register/", json={"email": "a@a.com", "password": "password1"})
    user_login = client.post("/login/", data={"username": "a@a.com", "password": "password1"})
    assert user_login.status_code == 200
    assert "access_token" in user_login.json()

def test_wrong_login(client):
    user_register = client.post("/register/", json={"email": "a@a.com", "password": "password1"})
    user_login = client.post("/login/", data={"username": "a@b.com", "password": "password1"})
    assert user_login.status_code == 401

def test_refresh(client):
    client.post("/register/", json={"email": "a@a.com", "password": "password1"})
    user_login = client.post("/login/", data={"username": "a@a.com", "password": "password1"})
    test_token = user_login.json()["refresh_token"]
    test_refresh_token = client.post("/refresh/", json={"refresh_token": test_token})
    assert test_refresh_token.status_code == 200
    assert "access_token" in test_refresh_token.json()

def test_refresh_with_invalid_token(client):
    test_wrong_token = client.post("/refresh/", json={"refresh_token": "not_a_token"})
    assert test_wrong_token.status_code == 401

def test_refresh_with_access_token(client):
    client.post("/register/", json={"email": "a@a.com", "password": "password1"})
    user_login = client.post("/login/", data={"username": "a@a.com", "password": "password1"})
    test_token = user_login.json()["access_token"]
    test_refresh_token = client.post("/refresh/", json={"refresh_token": test_token})
    assert test_refresh_token.status_code == 401