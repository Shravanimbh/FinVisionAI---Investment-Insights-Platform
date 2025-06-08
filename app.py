from flask import Flask, request, jsonify
import joblib
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load ML model and encoders
model = joblib.load('model.pkl')
risk_encoder = joblib.load('risk_encoder.pkl')
goal_encoder = joblib.load('goal_encoder.pkl')
product_encoder = joblib.load('product_encoder.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Transform input
        risk = risk_encoder.transform([data['risk']])[0]
        goal = goal_encoder.transform([data['goal']])[0]

        # Prepare model input
        X = [[risk, data['amount'], data['duration'], goal]]

        # Predict
        probabilities = model.predict_proba(X)[0]
        prediction = model.predict(X)[0]

        # Decode product
        decoded_prediction = product_encoder.inverse_transform([prediction])[0]
        confidence = round(max(probabilities) * 100, 2)

        return jsonify({
            'prediction': decoded_prediction,
            'confidence': confidence
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
