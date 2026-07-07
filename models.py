from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, nullable = False)
    hashed_password = Column(String, nullable = False)

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key = True, index = True)
    rawg_id = Column(Integer, unique = True)
    title = Column(String, nullable = False)
    genre = Column(String, nullable = True)
    release_date = Column(String, nullable = True)
    rawg_rating = Column(Float, nullable = False)

class UserGame(Base):
    __tablename__ = "usergames"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable = False)
    status = Column(String, nullable = False)
    user_rating = Column(Float, nullable = True)
    added_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))
