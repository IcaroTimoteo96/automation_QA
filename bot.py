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
INFO_FILE = "informacoes.txt"

# Inicializa o Flask
app = Flask(__name__)

def get_information(option):
    """Lê as informações do arquivo informacoes.txt e retorna o texto correto"""
    try:
        with open("informacoes.txt", "r", encoding="utf-8") as file:
            content = file.read()
            sections = content.split("\n\n")  # Divide as seções do arquivo
            for section in sections:
                if section.startswith(f"[{option}]"):
                    return section.replace(f"[{option}] ", "")
        return "Desculpe, não encontrei essa informação."
    except FileNotFoundError:
        return "Erro: arquivo de informações não encontrado."

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

                    if text in ["1", "2", "3"]:
                        info = get_information(text)
                        send_whatsapp_message(phone_number, info)
                    else:
                        menu_text = (
                        "Olá! Escolha uma das opções abaixo enviando o número correspondente:\n\n"
                        "1️⃣ - Data de Batismo\n"
                        "2️⃣ - Data de Crisma\n"
                        "3️⃣ - Dias ou Horários de confissões\n"
                        "4️⃣ - Falar com o atendimento")

                        send_whatsapp_message(phone_number, menu_text)

    return "OK", 200

# Função para enviar mensagem no WhatsApp
def send_whatsapp_message(to, message):
    """Envia mensagem pelo WhatsApp Cloud API."""
    recipient_id = format_phone_number(to)

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

def format_phone_number(phone_number):
    """Adiciona o '9' após o DDD se necessário"""
    if len(phone_number) == 12 and phone_number.startswith("55"):  # Verifica se é um número brasileiro sem o '9'
        return phone_number[:4] + "9" + phone_number[4:]
    return phone_number



# Inicia o servidor Flask
if __name__ == "__main__":
    app.run(port=5000, debug=True)
