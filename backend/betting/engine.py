"""
Sistema completo di Value Betting con Kelly Criterion e Bankroll Management
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValueBet:
    match_id: str
    home_team: str
    away_team: str
    outcome: str  # 'home', 'draw', 'away'
    probability: float  # Probabilità modello (0-1)
    market_odds: float  # Quota bookmaker
    fair_odds: float    # 1 / probability
    value: float        # (market_odds / fair_odds) - 1
    kelly_stake: float  # Percentuale bankroll
    expected_value: float
    confidence: float   # Confidenza modello
    bookmaker: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            "match_id": self.match_id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "outcome": self.outcome,
            "probability": round(self.probability, 4),
            "market_odds": self.market_odds,
            "fair_odds": round(self.fair_odds, 2),
            "value": round(self.value, 4),
            "value_percent": f"+{round(self.value * 100, 1)}%",
            "kelly_stake": f"{round(self.kelly_stake * 100, 2)}%",
            "expected_value": round(self.expected_value, 4),
            "confidence": round(self.confidence, 2),
            "bookmaker": self.bookmaker,
            "timestamp": self.timestamp.isoformat()
        }

class ValueBettingEngine:
    def __init__(self, 
                 min_value_threshold: float = 0.02,  # 2% minimo
                 min_confidence: float = 0.60,       # 60% confidenza
                 max_kelly_fraction: float = 0.25,   # Kelly frazionario (conservativo)
                 max_stake_per_bet: float = 0.05):   # Max 5% bankroll
        self.min_value = min_value_threshold
        self.min_confidence = min_confidence
        self.max_kelly_fraction = max_kelly_fraction
        self.max_stake = max_stake_per_bet
        
        # Bookmaker bias (adatta in base ai dati storici)
        self.bookmaker_bias = {
            "pinnacle": {"overround": 1.018, "reliability": 0.95},
            "bet365": {"overround": 1.042, "reliability": 0.90},
            "williamhill": {"overround": 1.045, "reliability": 0.88},
            "generic": {"overround": 1.05, "reliability": 0.85}
        }
    
    def calculate_fair_odds(self, probability: float) -> float:
        """Calcola quota equa (payout corretto)"""
        if probability <= 0 or probability >= 1:
            return 999.0
        return 1.0 / probability
    
    def calculate_kelly_stake(self, 
                             probability: float, 
                             odds: float,
                             confidence: float,
                             bankroll: float = 10000.0) -> Tuple[float, float]:
        """
        Calcola lo stake secondo Kelly Criterion frazionario
        
        Returns:
            (kelly_percentage, stake_amount)
        """
        # Kelly formula: f* = (bp - q) / b
        # b = odds - 1 (net odds received)
        # p = probability of winning
        # q = 1 - p
        
        b = odds - 1
        p = probability
        q = 1 - p
        
        # Edge
        edge = (b * p) - q
        
        if edge <= 0:
            return 0.0, 0.0
        
        # Kelly full
        kelly_full = edge / b
        
        # Kelly frazionario (conservativo)
        kelly_adj = kelly_full * self.max_kelly_fraction * confidence
        
        # Limita al massimo stake
        kelly_final = min(kelly_adj, self.max_kake_fraction)
        
        stake_amount = kelly_final * bankroll
        
        return kelly_final, stake_amount
    
    def calculate_expected_value(self, probability: float, odds: float) -> float:
        """
        EV = (Probability * Win) - (Loss Probability * Stake)
        Semplificato: EV = (p * (odds-1)) - (1-p)
        """
        return (probability * (odds - 1)) - (1 - probability)
    
    def adjust_odds_for_bias(self, 
                            odds: float, 
                            bookmaker: str,
                            outcome: str) -> float:
        """Adjusta le odds per il bias del bookmaker"""
        bias = self.bookmaker_bias.get(bookmaker, self.bookmaker_bias["generic"])
        
        # Rimuovi l'overround (margine bookmaker)
        adjusted = odds / bias["overround"]
        
        # Adjust per home bias (le squadre di casa sono spesso sottovalutate)
        if outcome == "home":
            adjusted *= 1.01  # Correzione lieve
        
        return adjusted
    
    def detect_value_bets(self,
                         predictions: List[Dict],
                         market_data: Dict[str, Dict],
                         bankroll: float = 10000.0) -> List[ValueBet]:
        """
        Analizza predizioni e quote di mercato per trovare value bets
        
        Args:
            predictions: Lista di predizioni del modello ML
            market_data: Dict {match_id: {bookmaker: {outcome: odds}}}
            bankroll: Bankroll attuale dell'utente
        """
        value_bets = []
        
        for pred in predictions:
            match_id = pred.get("match_id")
            match_name = pred.get("match_name", f"Match {match_id}")
            teams = match_name.split(" vs ")
            home_team = teams[0] if len(teams) > 0 else "Home"
            away_team = teams[1] if len(teams) > 1 else "Away"
            
            probs = pred.get("probabilities", {})
            confidence = pred.get("confidence", 0.5)
            
            # Estrai quote di mercato per questa partita
            match_odds = market_data.get(match_id, {})
            
            for outcome in ["home", "draw", "away"]:
                if outcome not in probs:
                    continue
                
                model_prob = probs[outcome]
                fair_odds = self.calculate_fair_odds(model_prob)
                
                # Cerca la miglior quota disponibile
                best_odds = 0.0
                best_bookmaker = "unknown"
                
                for bookmaker, outcomes in match_odds.items():
                    if outcome in outcomes:
                        odds = outcomes[outcome]
                        if odds > best_odds:
                            best_odds = odds
                            best_bookmaker = bookmaker
                
                if best_odds <= 1.0:
                    continue
                
                # Adjusta per bias bookmaker
                adjusted_odds = self.adjust_odds_for_bias(
                    best_odds, best_bookmaker, outcome
                )
                
                # Calcola value
                value = (adjusted_odds / fair_odds) - 1
                
                # Filtra per soglie
                if value < self.min_value or confidence < self.min_confidence:
                    continue
                
                # Calcola Kelly
                kelly_pct, stake_amount = self.calculate_kelly_stake(
                    model_prob, adjusted_odds, confidence, bankroll
                )
                
                if kelly_pct <= 0:
                    continue
                
                # Calcola EV
                ev = self.calculate_expected_value(model_prob, adjusted_odds)
                
                value_bet = ValueBet(
                    match_id=match_id,
                    home_team=home_team,
                    away_team=away_team,
                    outcome=outcome,
                    probability=model_prob,
                    market_odds=best_odds,
                    fair_odds=fair_odds,
                    value=value,
                    kelly_stake=kelly_pct,
                    expected_value=ev,
                    confidence=confidence,
                    bookmaker=best_bookmaker,
                    timestamp=datetime.utcnow()
                )
                
                value_bets.append(value_bet)
        
        # Ordina per value * confidence (ranking combinato)
        value_bets.sort(
            key=lambda x: x.value * x.confidence * (1 + x.expected_value), 
            reverse=True
        )
        
        logger.info(f"Rilevati {len(value_bets)} value bets su {len(predictions)} partite")
        return value_bets

# Singleton instance
betting_engine = ValueBettingEngine()