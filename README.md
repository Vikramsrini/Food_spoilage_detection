# Food Spoilage Detection Web App

This project is an end-to-end web application for predicting food spoilage using sensor data and machine learning. It features a Python Flask backend for model inference and a modern, responsive frontend for user interaction.

---

## Features

- **Machine Learning Model:** Predicts food spoilage using sensor readings (MQ8A, MQ135A, MQ9A, MQ4A, MQ2A, MQ3A).
- **REST API:** Flask backend exposes endpoints for prediction and health checks.
- **Responsive Web UI:** Clean, modern interface for entering sensor data and viewing results.
- **Easy Deployment:** Simple requirements and setup for both backend and frontend.

---

## Project Structure

```
Food spoilage/
├── Model/
│   ├── spoilage_rf_model.pkl
│   ├── requirements.txt
│   └── dataset
├── static/
│   ├── style.css
│   └── script.js
├── app.py
├── index.html
└── README.md
```

---

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/food-spoilage-detection.git
cd food-spoilage-detection
```

### 2. Backend Setup (Flask)

#### a. Create a virtual environment (recommended)

```sh
python3 -m venv .venv
source .venv/bin/activate
```

#### b. Install Python dependencies

```sh
pip install -r Model/requirements.txt
```

#### c. Make sure your trained model file (e.g., `spoilage_rf_model.pkl`) is in the `Model/` directory.

#### d. Run the Flask app

```sh
python app.py
```

The backend will be available at [http://localhost:5000](http://localhost:5000).

---

### 3. Frontend Setup

#### a. Open `index.html` in your browser

You can simply open the file, or serve it with a simple HTTP server:

```sh
# Python 3.x
python -m http.server 8000
```

Then visit [http://localhost:8000/index.html](http://localhost:8000/index.html).

---

## API Usage

### **POST** `/predict`

Send a JSON payload with sensor values:

```json
{
  "MQ8A": 320,
  "MQ135A": 450,
  "MQ9A": 410,
  "MQ4A": 390,
  "MQ2A": 470,
  "MQ3A": 510
}
```

**Response:**
```json
{
  "prediction": 1,
  "label": "Spoiled",
  "confidence": 0.92
}
```

---

## Requirements

See [`Model/requirements.txt`](Model/requirements.txt):

```
pandas
numpy
matplotlib
scikit-learn
joblib
flask
flask-cors
```

---

## Customization

- **Model:** Replace `spoilage_rf_model.pkl` with your own trained model if needed.
- **UI:** Edit `static/style.css` and `index.html` for custom branding or layout.
- **API:** Extend `app.py` for more endpoints or logic.

---

## License

MIT License

---

## Author

[Your Name]  
[Your GitHub Profile]

---

## Acknowledgements

- [scikit-learn](https://scikit-learn.org/)
-
