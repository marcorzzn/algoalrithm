from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ValueBet(BaseModel):
    match_id: str
    outcome: str
    probability: float
    market_odds: float
    value: float
    kelly_stake: float

@router.get("/value-bets")
async def get_value_bets():
    # Demo data
    return {
        "value_bets": [
            {
                "match_id": "match_1",
                "home_team": "Juventus",
                "away_team": "Inter",
                "outcome": "home",
                "probability": 0.52,
                "market_odds": 2.30,
                "fair_odds": 1.92,
                "value": 0.198,
                "kelly_stake": 0.043,
                "confidence": 0.72
            }
        ],
        "total": 1
    }