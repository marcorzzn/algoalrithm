def test_predict_endpoint(client):
    # Dati di test
    match_data = {
        "matches": [{
            "home_avg_xg": 1.8,
            "away_avg_xg": 1.2,
            "home_possession": 58.0,
            "away_possession": 42.0,
            "home_form": 1.7,
            "away_form": 1.2
        }]
    }
    
    response = client.post("/api/predictions/predict", json=match_data)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 1
    assert "probabilities" in data["predictions"][0]