from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.betting.engine import betting_engine, ValueBet
from backend.auth.security import get_current_active_user
from backend.auth.models import User
from backend.data.database.database import get_db

router = APIRouter()

class MarketOddsInput(BaseModel):
    match_id: str
    bookmaker: str
    home_odds: float
    draw_odds: float
    away_odds: float

class PredictionInput(BaseModel):
    match_id: str
    match_name: str
    probabilities: dict
    confidence: float

class ValueBetRequest(BaseModel):
    predictions: List[PredictionInput]
    market_data: List[MarketOddsInput]
    bankroll: float = 1000.0

@router.post("/detect", response_model=List[dict])
async def detect_value_bets(
    request: ValueBetRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint per rilevare value bets
    Richiede autenticazione
    """
    try:
        # Converti input nel formato atteso dall'engine
        market_dict = {}
        for odds in request.market_data:
            if odds.match_id not in market_dict:
                market_dict[odds.match_id] = {}
            
            market_dict[odds.match_id][odds.bookmaker] = {
                "home": odds.home_odds,
                "draw": odds.draw_odds,
                "away": odds.away_odds
            }
        
        # Usa bankroll utente se configurato
        user_bankroll = current_user.betting_config.get("initial_bankroll", request.bankroll)
        
        # Rileva value bets
        value_bets = betting_engine.detect_value_bets(
            predictions=[p.dict() for p in request.predictions],
            market_data=market_dict,
            bankroll=user_bankroll
        )
        
        return [bet.to_dict() for bet in value_bets]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_betting_history(
    current_user: User = Depends(get_current_active_user),
    limit: int = 50
):
    """
    Recupera storico scommesse dell'utente
    """
    # Qui andrebbe implementata la query al DB
    return {
        "user_id": str(current_id),
        "bets": [],
        "total": 0
    }

@router.post("/place-bet")
async def place_bet(
    bet_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registra una scommessa piazzata
    """
    # Logica per salvare la scommessa nel DB
    # E inviare notifica WebSocket
    from backend.api.websocket.manager import notify_new_value_bet
    
    await notify_new_value_bet(bet_data)
    
    return {"status": "success", "message": "Bet registered"}