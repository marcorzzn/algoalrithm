from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import predictions, betting, health
from backend.auth.router import router as auth_router
# Aggiungi import
from backend.api.websocket.router import router as ws_router



app = FastAPI(title="Football Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aggiungi questo import

# Aggiungi questo prima degli altri include_router
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(betting.router, prefix="/api/betting", tags=["betting"])

# Aggiungi router (senza prefix per WebSocket)
app.include_router(ws_router)

@app.get("/")
async def root():
    return {
        "app": "Football Analytics Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "predict": "/api/predictions/predict",
            "value_bets": "/api/betting/value-bets"
        }
    }