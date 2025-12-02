from pathlib import Path
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import traceback
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Local import of your predictor
from car_price_predictor import CarPricePredictor

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Configurable model paths via environment variables
MODEL_PATH = os.environ.get("MODEL_PATH", "models/extra_trees_tuned.pkl")
ENCODERS_PATH = os.environ.get("ENCODERS_PATH", "models/encoders.pkl")

predictor = None
init_error = None

def try_init_predictor():
    global predictor, init_error
    try:
        predictor = CarPricePredictor(model_path=MODEL_PATH, encoders_path=ENCODERS_PATH)
        init_error = None
    except Exception as e:
        predictor = None
        init_error = str(e)
        app.logger.error("Failed to initialize CarPricePredictor: %s", init_error)
        app.logger.debug(traceback.format_exc())

# Initialize on startup
try_init_predictor()


@app.route("/")
def index():
    if predictor is None:
        return (
            "<h2>CarPricePredictor not initialized</h2>"
            f"<pre>{init_error}</pre>"
            "<p>Ensure model files exist under <code>models/</code> or set MODEL_PATH/ENCODERS_PATH.</p>"
        ), 500

    return render_template(
        "index.html",
        marques=predictor.marques_acceptees,
        energies=['Diesel', 'Essence', 'Hybride', 'Electrique', 'GPL'],
        boites=['Manuelle', 'Automatique']
    )


@app.route("/health", methods=["GET"])
def health():
    if predictor is None:
        return jsonify({"healthy": False, "error": init_error}), 500
    return jsonify({"healthy": True}), 200


@app.route("/api/brands", methods=["GET"])
def api_brands():
    if predictor is None:
        return jsonify({"success": False, "error": "Predictor not initialized"}), 500

    return jsonify({
        "success": True,
        "marques": predictor.marques_acceptees,
        "luxury_brands": predictor.luxury_brands,
        "brand_categories": predictor.brand_categories,
        "energies": ['Diesel', 'Essence', 'Hybride', 'Electrique', 'GPL'],
        "boites": ['Manuelle', 'Automatique']
    })


@app.route("/api/predict", methods=["POST"])
def api_predict():
    if predictor is None:
        return jsonify({"success": False, "error": "Predictor not initialized"}), 500

    try:
        payload = request.get_json(force=True)
        required = ['marque', 'modele', 'annee', 'kilometrage', 'energie', 'boite_vitesses', 'puissance_fiscale']
        missing = [k for k in required if k not in payload]
        if missing:
            return jsonify({"success": False, "error": f"Missing fields: {missing}"}), 400

        # Type conversions and basic validation
        marque = payload['marque']
        modele = payload.get('modele', '')
        annee = int(payload['annee'])
        kilometrage = float(payload['kilometrage'])
        energie = payload['energie']
        boite_vitesses = payload['boite_vitesses']
        puissance_fiscale = int(payload['puissance_fiscale'])

        result = predictor.predict(
            marque=marque,
            modele=modele,
            annee=annee,
            kilometrage=kilometrage,
            energie=energie,
            boite_vitesses=boite_vitesses,
            puissance_fiscale=puissance_fiscale
        )

        status = 200 if result.get("success", False) else 400
        return jsonify(result), status

    except Exception as e:
        app.logger.error("Error in /api/predict: %s", str(e))
        app.logger.debug(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/predict_batch", methods=["POST"])
def api_predict_batch():
    if predictor is None:
        return jsonify({"success": False, "error": "Predictor not initialized"}), 500

    try:
        payload = request.get_json(force=True)
        vehicles = payload.get("vehicles")
        if not isinstance(vehicles, list):
            return jsonify({"success": False, "error": 'Field "vehicles" must be a list'}), 400

        results = predictor.predict_batch(vehicles)
        return jsonify({"success": True, "results": results}), 200

    except Exception as e:
        app.logger.error("Error in /api/predict_batch: %s", str(e))
        app.logger.debug(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # When running locally, this starts a debug server. Use gunicorn/waitress in production.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")