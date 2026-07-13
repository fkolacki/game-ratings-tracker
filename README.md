# Game Ratings Tracker

A backend API built with FastAPI where you can track games you've played, rate them, and organize them into a personal list (planned / playing / completed). Game data (title, genre, release date, RAWG rating) is pulled from the [RAWG Video Games API](https://rawg.io/apidocs) and synced into a local database.

This project was a way to practice writing real backend logic myself: a proper many-to-many relationship, and an integration with an external API, instead of just doing CRUD on my own data.

## What it does

- Register / log in (JWT auth, passwords hashed with bcrypt)
- Pull games from RAWG and store them locally, so you're not hitting the external API on every request
- Add games to your own list, with a status and an optional rating
- Update the status/rating later
- Filter the game catalog by genre, minimum rating, or release year
- Get a quick summary of your list (how many games, how many completed, your average rating)

## Stack

Python, FastAPI, SQLAlchemy, PostgreSQL, Pydantic, JWT (python-jose), bcrypt (passlib), pytest for testing, httpx for the RAWG requests, pydantic-settings for config. Running with Docker Compose.

## How the data is structured

Three tables. `User` and `Game` are pretty standard, but `UserGame` is the interesting one. It's a many-to-many relationship between users and games, except it also needs to store extra info (status, your personal rating, when you added it), so it's a full model instead of a plain join table.

```
User <  UserGame  > Game
```

## Running it with Docker

You'll need a `.env` file with:
```
SECRET_KEY=your_own_random_secret
RAWG_API_KEY=your_rawg_api_key
DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@db:5432/your_postgres_db
POSTGRES_DB=your_postgres_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
```

(RAWG API keys are free, get one [here](https://rawg.io/apidocs).)

```bash
git clone https://github.com/fkolacki/game-ratings-tracker.git
cd game-ratings-tracker
docker compose up --build
```

Docs at `http://localhost:8000/docs`.


## Running tests

**One-time setup:**

Create a `.env.test` file (same format as `.env`, but pointing to a separate test database):
```
SECRET_KEY=your_own_random_secret
RAWG_API_KEY=your_rawg_api_key
DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@localhost:5432/your_test_db_name
```

With the containers running (`docker compose up -d`), create the test database once (connecting to your existing `your_postgres_db` database, from which you'll create the new one):
```bash
docker exec -it game-ratings-tracker-db-1 psql -U your_postgres_user -d your_postgres_db
```
```sql
CREATE DATABASE your_test_db_name;
```

**Running the tests:**

With the containers up, just run:
```bash
python -m pytest
```

Tests use a separate database from the one the app runs on, and each test starts with a clean slate (tables are dropped and recreated before every test).


## Endpoints

**Auth**
- `POST /register/`: create an account
- `POST /login/`: log in, get a JWT back

**Games**
- `POST /games/sync`: pull games from RAWG into the local DB (updates existing ones instead of duplicating them)
- `GET /games/`: list games, optionally filter by `genre`, `min_rating`, `year`

**My list** (all of these need a valid token)
- `POST /me/games/{game_id}/`: add a game to your list
- `GET /me/games/`: see your list
- `PATCH /me/games/{game_id}/`: update status/rating
- `GET /me/stats/`: summary stats (total games, count per status, average rating)

## A couple of things worth explaining

**Why `/games/sync` doesn't create duplicates.** It checks if a game with that `rawg_id` already exists before deciding to insert or update. So you can call it as many times as you want without ending up with the same game twice.

**Why `UserGame` is a full model and not just a join table.** It needs to hold more than just the two foreign keys. Status, rating, and timestamp all live on that row.

**Why `user_rating` is a float, not an int.** I rate games with half points sometimes (like a 7.5), so an integer felt too limiting.

**Why the Dockerfile has multiple stages.** I split the Dockerfile into three stages (`base`, `dev`, `production`) so the production image doesn't have to install testing tools that the app doesn't need in production. The `dev` stage additionally installs `pytest`, while `production` only includes what the app needs to run.

**Secrets aren't hardcoded.** `SECRET_KEY` and `RAWG_API_KEY` come from `.env`, which is gitignored and also excluded from the Docker build.

## Next steps

- More test coverage - right now only auth is tested, games and the user's list endpoints still need it
- Caching frequently-requested game listings with Redis instead of hitting Postgres every time
- Pagination on the list endpoints
- Refresh tokens
- Actually deploying it somewhere instead of just running it locally

## Note

Built entirely by me - models, auth, the RAWG integration, tests, Docker setup. I used Claude.ai along the way to check my understanding and unblock myself when stuck, similar to how I'd use documentation or Stack Overflow.