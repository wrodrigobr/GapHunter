from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    nickname: str

class UserCreate(UserBase):
    password: str
    # Informações específicas de poker
    poker_experience: Optional[str] = None  # "beginner", "intermediate", "advanced", "professional"
    preferred_games: Optional[str] = None   # "cash", "tournaments", "both"
    main_stakes: Optional[str] = None       # "micro", "low", "mid", "high"
    poker_goals: Optional[str] = None       # "recreational", "profit", "professional"
    country: Optional[str] = None
    timezone: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    poker_experience: Optional[str] = None
    preferred_games: Optional[str] = None
    main_stakes: Optional[str] = None
    poker_goals: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Hand schemas
class HandBase(BaseModel):
    hand_id: str
    tournament_id: Optional[str] = None
    table_name: Optional[str] = None
    date_played: Optional[datetime] = None
    hero_name: Optional[str] = None
    hero_position: Optional[str] = None
    hero_cards: Optional[str] = None
    hero_action: Optional[str] = None
    pot_size: Optional[float] = None
    bet_amount: Optional[float] = None
    board_cards: Optional[str] = None
    raw_hand: str
    ai_analysis: Optional[str] = None

class HandCreate(HandBase):
    pass

class Hand(HandBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Upload response
class UploadResponse(BaseModel):
    message: str
    hands_processed: int
    hands: List[Hand]

