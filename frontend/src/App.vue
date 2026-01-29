<template>
  <div class="app">
    <header>
      <h1>⚽ Football Analytics Platform</h1>
    </header>
    
    <main>
      <div class="card">
        <h2>Predizione Match</h2>
        <div class="form-group">
          <label>Home xG:</label>
          <input v-model="features.home_avg_xg" type="number" step="0.1" />
        </div>
        <div class="form-group">
          <label>Away xG:</label>
          <input v-model="features.away_avg_xg" type="number" step="0.1" />
        </div>
        <div class="form-group">
          <label>Home Possession:</label>
          <input v-model="features.home_possession" type="number" />
        </div>
        <button @click="predict" :disabled="loading">
          {{ loading ? 'Analisi...' : 'Predici' }}
        </button>
        
        <div v-if="prediction" class="results">
          <h3>Risultati:</h3>
          <div class="prob-bar">
            <div class="home" :style="{width: prediction.probabilities.home * 100 + '%'}">
              Casa {{ (prediction.probabilities.home * 100).toFixed(1) }}%
            </div>
            <div class="draw" :style="{width: prediction.probabilities.draw * 100 + '%'}">
              X {{ (prediction.probabilities.draw * 100).toFixed(1) }}%
            </div>
            <div class="away" :style="{width: prediction.probabilities.away * 100 + '%'}">
              Trasferta {{ (prediction.probabilities.away * 100).toFixed(1) }}%
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      features: {
        home_avg_xg: 1.8,
        away_avg_xg: 1.2,
        home_possession: 58,
        away_possession: 42,
        home_form: 1.7,
        away_form: 1.2
      },
      prediction: null,
      loading: false
    }
  },
  methods: {
    async predict() {
      this.loading = true
      try {
        const response = await axios.post('http://localhost:8000/api/predictions/predict', {
          matches: [this.features]
        })
        this.prediction = response.data.predictions[0]
      } catch (error) {
        alert('Errore: ' + error.message)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style>
.app {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

.card {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background: #2563eb;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
}

button:hover {
  background: #1d4ed8;
}

.results {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 4px;
}

.prob-bar {
  display: flex;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 10px;
  color: white;
  text-align: center;
  line-height: 40px;
  font-size: 14px;
}

.home { background: #2563eb; }
.draw { background: #6b7280; }
.away { background: #dc2626; }
</style>