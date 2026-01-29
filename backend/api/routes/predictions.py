# backend/api/routes/predictions.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import numpy as np
import pickle
import os
from config import settings

router = APIRouter()

# Carica modello se esiste
model = None
try:
    model_path = os.path.join(settings.ML_MODELS_PATH, "demo_model.pkl")
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            print(f"✅ Model loaded from {model_path}")
except Exception as e:
    print(f"⚠️  Model not loaded: {e}")

# Schemi Pydantic per validazione
class MatchFeatures(BaseModel):
    home_avg_xg: float
    away_avg_xg: float
    home_possession: float
    away_possession: float
    home_form: float
    away_form: float

class PredictionRequest(BaseModel):
    matches: List[MatchFeatures]

class PredictionResponse(BaseModel):
    probabilities: dict
    confidence: float
    model_type: str

@router.post("/predict", response_model=List[PredictionResponse])
async def predict(request: PredictionRequest):
    """
    Endpoint per predizioni ML su partite di calcio
    """
    try:
        if model is None:
            # Risposta demo se il modello non è caricato
            return [
                {
                    "probabilities": {
                        "home": 0.45,
                        "draw": 0.25,
                        "away": 0.30
                    },
                    "confidence": 0.75,
                    "model_type": "demo"
                }
                for _ in request.matches
            ]
        
        # Prepara dati per il modello
        features = []
        for match in request.matches:
            features.append([
                match.home_avg_xg,
                match.away_avg_xg,
                match.home_possession,
                match.away_possession,
                match.home_form,
                match.away_form
            ])
        
        X = np.array(features)
        probs = model.predict_proba(X)
        
        # Formatta risposta
        predictions = []
        for prob in probs:
            predictions.append({
                "probabilities": {
                    "home": round(float(prob[0]), 3),
                    "draw": round(float(prob[1]), 3),
                    "away": round(float(prob[2]), 3)
                },
                "confidence": round(float(np.max(prob)), 3),
                "model_type": "xgboost"
            })
        
        return predictions
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
async def model_info():
    """Info sul modello caricato"""
    return {
        "loaded": model is not None,
        "model_type": "xgboost" if model else "none",
        "features": ["home_avg_xg", "away_avg_xg", "home_possession", 
                    "away_possession", "home_form", "away_form"]
    }