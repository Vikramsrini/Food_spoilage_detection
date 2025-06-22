from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
MODEL_DIR = os.path.join(os.path.dirname(__file__), "Model")
MODEL_FILE = "realistic_spoilage_model.joblib"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)
FEATURES = ['MQ8A', 'MQ135A', 'MQ9A', 'MQ4A', 'MQ2A', 'MQ3A']
SENSOR_RANGE = (0, 1023)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FoodSpoilageModel:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model with comprehensive error handling"""
        try:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
            
            self.model = joblib.load(MODEL_PATH)
            
            # Test model functionality
            test_input = [[300] * len(FEATURES)]  # Mid-range test values
            _ = self.model.predict(test_input)
            _ = self.model.predict_proba(test_input)
            
            logger.info("Model loaded and validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            self.model = None
            return False
    
    def validate_input(self, data):
        """Validate input data structure and values"""
        errors = []
        
        # Check for missing features
        missing_features = [f for f in FEATURES if f not in data]
        if missing_features:
            errors.append(f"Missing features: {', '.join(missing_features)}")
        
        # Validate each feature value
        for feature in FEATURES:
            if feature in data:
                try:
                    value = float(data[feature])
                    if not (SENSOR_RANGE[0] <= value <= SENSOR_RANGE[1]):
                        errors.append(
                            f"{feature} value {value} out of range "
                            f"({SENSOR_RANGE[0]}-{SENSOR_RANGE[1]})"
                        )
                except (ValueError, TypeError):
                    errors.append(f"Invalid value for {feature}: {data[feature]}")
        
        return not bool(errors), errors

# Initialize model
spoilage_model = FoodSpoilageModel()

@app.route("/", methods=["GET"])
def home():
    """API home endpoint"""
    return jsonify({
        "status": "operational",
        "model_loaded": spoilage_model.model is not None,
        "endpoints": {
            "/predict": "POST - Predict food spoilage from sensor data",
            "/health": "GET - API health check",
            "/features": "GET - List of required features"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy" if spoilage_model.model else "degraded",
        "model_loaded": spoilage_model.model is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/features", methods=["GET"])
def list_features():
    """Endpoint to list required features"""
    return jsonify({
        "required_features": FEATURES,
        "value_range": f"{SENSOR_RANGE[0]}-{SENSOR_RANGE[1]}"
    })

@app.route("/predict", methods=["POST"])
def predict():
    """Main prediction endpoint"""
    # Check model availability
    if not spoilage_model.model:
        logger.error("Prediction attempted with no model loaded")
        return jsonify({
            "error": "Model not available",
            "suggestion": "Check server logs and model file"
        }), 503
    
    # Get and validate input data
    data = request.get_json()
    if not data:
        logger.warning("Empty request received")
        return jsonify({"error": "No input data provided"}), 400
    
    is_valid, validation_errors = spoilage_model.validate_input(data)
    if not is_valid:
        logger.warning(f"Invalid input: {validation_errors}")
        return jsonify({
            "error": "Input validation failed",
            "details": validation_errors
        }), 400
    
    try:
        # Prepare input data
        input_data = [data[feature] for feature in FEATURES]
        input_df = pd.DataFrame([input_data], columns=FEATURES)
        
        # Make prediction
        prediction = int(spoilage_model.model.predict(input_df)[0])
        probabilities = spoilage_model.model.predict_proba(input_df)[0]
        confidence = float(np.max(probabilities))
        
        # Prepare response
        response = {
            "prediction": prediction,
            "label": "Spoiled" if prediction == 1 else "Fresh",
            "confidence": confidence,
            "probabilities": {
                "fresh": float(probabilities[0]),
                "spoiled": float(probabilities[1])
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Prediction successful: {response}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Prediction failed",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    # Start the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=True)