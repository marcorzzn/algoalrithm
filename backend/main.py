from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import predictions, betting, health

app = FastAPI(title="Football Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(betting.router, prefix="/api/betting", tags=["betting"])

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