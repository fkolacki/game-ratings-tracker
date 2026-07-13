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