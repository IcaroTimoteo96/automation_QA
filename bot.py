import os
import json
import requests
import flask
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv() #Carregar variáveis do arquivo .env

# Configurações da API do WhatsApp Cloud
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")

# Nome do arquivo de datas
BAPTISM_FILE = "batismo.txt"

# Inicializa o Flask
app = Flask(__name__)

# Função para ler as datas do arquivo
def get_baptism_dates():
    """Lê as datas do arquivo .txt e retorna o texto para o WhatsApp."""
    if not os.path.exists(BAPTISM_FILE):
        return "Ainda não há datas de batismo cadastradas."

    with open(BAPTISM_FILE, "r", encoding="utf-8") as file:
        return file.read()

# Webhook para verificação do WhatsApp Cloud API
@app.route("/webhook", methods=["GET"])
def webhook_verify():
    """Verifica a configuração do Webhook no Meta Developer."""
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Erro de verificação", 403

# Webhook para receber mensagens do WhatsApp
@app.route("/webhook", methods=["POST"])
def webhook_receive():
    """Recebe mensagens do WhatsApp e responde automaticamente."""

    data = request.get_json()
    print("request", data)
    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for message in entry.get("changes", []):
                message_data = message.get("value", {}).get("messages", [])
                if message_data:
                    message_info = message_data[0]
                    phone_number = message_info["from"]
                    text = message_info["text"]["body"].lower()

                    # Verifica palavras-chave na mensagem
                    if "batismo" in text:
                        reply = get_baptism_dates()
                    else:
                        reply = "Desculpe, não entendi. Digite 'batismo' para saber mais."

                    # Enviar resposta pelo WhatsApp
                    send_whatsapp_message(phone_number, reply)

    return "OK", 200

# Função para enviar mensagem no WhatsApp
def send_whatsapp_message(to, message):
    """Envia mensagem pelo WhatsApp Cloud API."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

# Inicia o servidor Flask
if __name__ == "__main__":
    app.run(port=5000, debug=True)
