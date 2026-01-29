from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
import pickle
import os
from config import settings

router = APIRouter()

# Carica modello demo se esiste
model = None
try:
    model_path = os.path.join(settings.ML_MODELS_PATH, "demo_model.pkl")
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
except Exception as e:
    print(f"Model not loaded: {e}")

class MatchFeatures(BaseModel):
    home_avg_xg: float
    away_avg_xg: float
    home_possession: float
    away_possession: float
    home_form: float
    away_form: float

class PredictionRequest(BaseModel):
    matches: List[MatchFeatures]

@router.post("/predict")
async def predict(request: PredictionRequest):
    try:
        if model is None:
            # Risposta demo se non c'è il modello
            return {
                "predictions": [{
                    "probabilities": {
                        "home": 0.45,
                        "draw": 0.25,
                        "away": 0.30
                    },
                    "confidence": 0.75,
                    "model_type": "demo"
                }]
            }
        
        # Prepara dati
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
        
        predictions = []
        for prob in probs:
            predictions.append({
                "probabilities": {
                    "home": float(prob[0]),
                    "draw": float(prob[1]),
                    "away": float(prob[2])
                },
                "confidence": float(np.max(prob)),
                "model_type": "xgboost"
            })
        
        return {"predictions": predictions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))