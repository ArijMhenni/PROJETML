import React from 'react'
import PredictionForm from './components/PredictionForm'

export default function App() {
  return (
    <div className="app">
      <header className="hero">
        <div className="hero-inner">
          <h1>Car Price Predictor</h1>
          <p className="tagline">Estimate vehicle prices in seconds — powered by your ExtraTrees model.</p>
        </div>
      </header>

      <main className="container">
        <section className="left">
          <PredictionForm />
        </section>

        <aside className="right">
          <div className="card help">
            <h3>How it works</h3>
            <ol>
              <li>Choose a brand, model and year</li>
              <li>Enter kilometrage and technical info</li>
              <li>Submit to get an estimated price and a confidence range</li>
            </ol>
            <p className="muted">The app calls your Flask backend (/api/predict). Make sure your server is running (default http://localhost:5000).</p>
          </div>

          <div className="card tips">
            <h3>Tips</h3>
            <ul>
              <li>Use realistic kilometrage & year for best estimates</li>
              <li>If a brand isn't listed, add it to the model encoders as OTHER_BRAND</li>
            </ul>
          </div>
        </aside>
      </main>

      <footer className="footer">
        <small>Built for the Car Price ML project — React + Flask</small>
      </footer>
    </div>
  )
}