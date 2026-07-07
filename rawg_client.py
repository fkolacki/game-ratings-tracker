from config import settings
import httpx

URL = "https://api.rawg.io/api/games"

def fetch_games(page: int = 1):
    params = {"key": settings.rawg_api_key, "dates": "2021-01-01,2026-12-31", "page": page, "page_size": 40, "ordering": "-rating"}
    response = httpx.get(URL, params = params)
    return response.json()

if __name__ == "__main__":
    data = fetch_games()
    print(data["results"])