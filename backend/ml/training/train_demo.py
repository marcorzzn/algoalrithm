import numpy as np
import pandas as pd
import pickle
import os
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss

def generate_data(n_samples=5000):
    """Genera dati sintetici realistici"""
    np.random.seed(42)
    
    data = {
        'home_avg_xg': np.random.normal(1.5, 0.4, n_samples),
        'away_avg_xg': np.random.normal(1.2, 0.4, n_samples),
        'home_possession': np.random.normal(55, 8, n_samples),
        'away_possession': np.random.normal(45, 8, n_samples),
        'home_form': np.random.normal(1.6, 0.5, n_samples),
        'away_form': np.random.normal(1.3, 0.5, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Calcola forza relativa
    home_strength = (df['home_avg_xg'] + df['home_possession']/100 + df['home_form']) / 3
    away_strength = (df['away_avg_xg'] + df['away_possession']/100 + df['away_form']) / 3
    
    # Genera risultati
    home_prob = home_strength / (home_strength + away_strength + 0.4)
    away_prob = away_strength / (home_strength + away_strength + 0.4)
    draw_prob = 0.4 / (home_strength + away_strength + 0.4)
    
    # Normalizza
    total = home_prob + draw_prob + away_prob
    home_prob /= total
    draw_prob /= total
    away_prob /= total
    
    probs = np.vstack([home_prob, draw_prob, away_prob]).T
    y = np.array([np.random.choice([0,1,2], p=p) for p in probs])
    
    return df, y

def main():
    print("🚀 Training modello demo...")
    
    # Genera dati
    X, y = generate_data(10000)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        objective='multi:softprob',
        num_class=3
    )
    
    model.fit(X_train, y_train)
    
    # Valuta
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    loss = log_loss(y_test, y_proba)
    
    print(f"✅ Accuracy: {acc:.3f}")
    print(f"✅ Log Loss: {loss:.3f}")
    
    # Salva
    os.makedirs('data/models', exist_ok=True)
    with open('data/models/demo_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("💾 Modello salvato in data/models/demo_model.pkl")

if __name__ == "__main__":
    main()