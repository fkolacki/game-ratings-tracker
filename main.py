from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from database import Base, engine, get_db
from sqlalchemy.orm import Session
from typing import List, Optional
import auth
import schemas
import models
import rawg_client

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/register/", response_model = schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code = 400, detail = "Email already registered")
    new_user = models.User(email = user_in.email, hashed_password = auth.hash_password(user_in.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login/", response_model = schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    find_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if find_user is None or not auth.verify_password(form_data.password, find_user.hashed_password):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Email or password are incorrect")
    access_token = auth.create_access_token(find_user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/games/sync")
def games(db: Session = Depends(get_db)):
    data = rawg_client.fetch_games()
    games_list = data["results"]
    for game_data in games_list:
        genres_names = [genre["name"] for genre in game_data.get("genres", [])]
        genres_str = ", ".join(genres_names)
        existing_game = db.query(models.Game).filter(models.Game.rawg_id == game_data["id"]).first()
        if existing_game:
            existing_game.title = game_data["name"]
            existing_game.genre = genres_str
            existing_game.release_date = game_data["released"]
            existing_game.rawg_rating = game_data.get("rating", 0)
        else:
            new_game = models.Game(rawg_id = game_data["id"], title = game_data["name"], genre = genres_str, release_date = game_data["released"], rawg_rating = game_data.get("rating", 0))
            db.add(new_game)
    db.commit()
    return {"message": f"Synced {len(games_list)} games"}

@app.post("/me/games/{game_id}/", response_model = schemas.UserGameOut)
def add_game_to_list(game_id: int, user_game_in: schemas.UserGameCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    existing_game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if existing_game is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Game doesn't exist")
    new_user_game = models.UserGame(user_id = current_user.id, game_id = game_id, status = user_game_in.status, user_rating = user_game_in.user_rating)
    db.add(new_user_game)
    db.commit()
    db.refresh(new_user_game)
    return new_user_game

@app.get("/me/games/", response_model = List[schemas.UserGameOut])
def my_list(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    my_games = db.query(models.UserGame).filter(models.UserGame.user_id == current_user.id).all()
    return my_games

@app.patch("/me/games/{game_id}/", response_model = schemas.UserGameOut)
def update_user_game(game_id: int, updates: schemas.UserGameUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    user_game_entry = db.query(models.UserGame).filter(models.UserGame.id == game_id, models.UserGame.user_id == current_user.id).first()
    if user_game_entry is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Game doesn't exist")
    for field, value in updates.model_dump(exclude_unset = True).items():
        setattr(user_game_entry, field, value)

    db.commit()
    db.refresh(user_game_entry)
    return user_game_entry

@app.get("/games/", response_model = List[schemas.GameOut])
def get_games(genre: Optional[str] = None, min_rating: Optional[float] = None, year: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Game)
    if genre:
        query = query.filter(models.Game.genre.like(f"%{genre}%"))
    if min_rating:
        query = query.filter(models.Game.rawg_rating >= min_rating)
    if year:
        query = query.filter(models.Game.release_date.like(f"{year}%"))
    return query.all()

@app.get("/me/stats/")
def my_stats (current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    user_stats = db.query(models.UserGame).filter(models.UserGame.user_id == current_user.id).all()
    total_games = len(user_stats)
    planned_count = len([entry for entry in user_stats if entry.status == "planned"])
    playing_count = len([entry for entry in user_stats if entry.status == "playing"])
    completed_count = len([entry for entry in user_stats if entry.status == "completed"])
    ratings = ([entry.user_rating for entry in user_stats if entry.user_rating is not None])
    if ratings:
        user_rating_avg = sum(ratings) / len(ratings)
    else:
        user_rating_avg = None
    return {"total_games": total_games, "planned": planned_count, "playing": playing_count, "completed": completed_count, "user_rating_avg": user_rating_avg if user_rating_avg is not None else 0}
