from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):

    model_config = ConfigDict(from_attributes = True)

    id: int
    email: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenCreate(BaseModel):
    refresh_token: str

class UserGameCreate(BaseModel):
    status: str
    user_rating: Optional[float] = None

class UserGameOut(BaseModel):

    model_config = ConfigDict(from_attributes = True)

    id: int
    game_id: int
    status: str
    user_rating: Optional[float] = None
    added_at: datetime

class UserGameUpdate(BaseModel):

    status: Optional[str] = None
    user_rating: Optional[float] = None

class GameOut(BaseModel):

    model_config = ConfigDict(from_attributes = True)

    id: int
    rawg_id: int
    title: str
    genre: Optional[str] = None
    release_date: Optional[str] = None
    rawg_rating: float