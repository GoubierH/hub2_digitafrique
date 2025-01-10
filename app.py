import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Remplacer par l'URL de base de l'API Hub2
HUB2_API_BASE_URL = "https://api.hub2.io"

# Récupérer la clé API depuis les variables d'environnement définies sur Qoddi
API_KEY = os.getenv("HUB2_API_KEY")

# Vérifier si la clé API est bien définie
if not API_KEY:
    raise ValueError("API_KEY is not set in the environment variables")

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Hello from Flask!"})


@app.route('/payment', methods=['POST'])
def create_payment_intent():
    print("Requête reçue sur /create_payment_intent")  # Confirme que la route est atteinte
    print(f"Données reçues : {request.json}")         # Affiche les données envoyées
    
    data = request.json  # Récupérer les données JSON envoyées
    customer_reference = data.get("customerReference")
    purchase_reference = data.get("purchaseReference")
    amount = data.get("amount")
    currency = data.get("currency")

    # Vérifier la présence des données nécessaires
    if not all([customer_reference, purchase_reference, amount, currency]):
        return jsonify({"error": "Missing required fields"}), 400

    # Créer la PaymentIntent via l'API Hub2
    payload = {
        "customerReference": customer_reference,
        "purchaseReference": purchase_reference,
        "amount": amount,
        "currency": currency
    }

    headers = {
        "ApiKey": API_KEY,
        "Content-Type": "application/json"
    }

    print(f"Payload envoyé : {payload}")
    response = requests.post(HUB2_API_BASE_URL, headers=headers, json=payload)

    print(f"Réponse de l'API Hub2 : {response.status_code}, {response.text}")
    
    if response.status_code == 200:
        return jsonify(response.json())  # Retourner les données de la PaymentIntent créée
    else:
        return jsonify({"error": "Failed to create PaymentIntent", "details": response.json()}), 500


@app.route('/test', methods=['POST'])
def test_post():
    return jsonify({"message": "POST request fonctionne"})


# Route pour vérifier le statut d'un paiement
@app.route('/check_payment_status/<payment_intent_id>', methods=['GET'])
def check_payment_status(payment_intent_id):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{HUB2_API_BASE_URL}/{payment_intent_id}", headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to retrieve payment status", "details": response.json()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=False)