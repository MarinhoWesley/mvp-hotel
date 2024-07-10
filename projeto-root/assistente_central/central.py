import os
import sys

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from common.database import carregar_dados_usuarios
import openai
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from langdetect import detect, LangDetectException

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Acessar as chaves de API
openai.api_key = os.getenv('OPENAI_API_KEY')
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')

# Inicializar o cliente Twilio
client = Client(twilio_account_sid, twilio_auth_token)

app = Flask(__name__)

user_state = {}

# Função para identificar o idioma da mensagem
def identificar_idioma(mensagem):
    saudacoes_pt = ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite']
    saudacoes_en = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening']

    mensagem_lower = mensagem.lower()

    if any(saudacao in mensagem_lower for saudacao in saudacoes_pt):
        return 'pt'
    elif any(saudacao in mensagem_lower for saudacao in saudacoes_en):
        return 'en'
    else:
        try:
            idioma = detect(mensagem)
        except LangDetectException:
            idioma = 'pt'
        return idioma

# Função para validar usuário
def validar_usuario(numero, senha, dados_usuarios):
    usuario = dados_usuarios[(dados_usuarios['NUM'] == numero) & (dados_usuarios['SENHA'] == senha)]
    if not usuario.empty:
        return usuario.iloc[0]['NÍVEL DE ACESSO']
    return None

# Função para obter a resposta da OpenAI
def get_openai_response(prompt, lang='pt', model='gpt-4o'):
    system_message = "Você é o Assistente Virtual do hotel. Como posso ajudar?" if lang == 'pt' else "You are the Virtual Assistant of the hotel. How can I help?"
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

# Endpoint principal para receber mensagens
@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    user_id = request.values.get('From', '').strip()

    if user_id not in user_state:
        # Detectar o idioma
        idioma = identificar_idioma(incoming_msg)
        user_state[user_id] = {'step': 'ask_credentials', 'lang': idioma}
        response_text = "Por favor, forneça seu número de matrícula." if idioma == 'pt' else "Please provide your registration number."
    elif user_state[user_id]['step'] == 'ask_credentials':
        user_state[user_id]['numero'] = incoming_msg
        user_state[user_id]['step'] = 'ask_password'
        idioma = user_state[user_id]['lang']
        response_text = "Agora, por favor, forneça sua senha." if idioma == 'pt' else "Now, please provide your password."
    elif user_state[user_id]['step'] == 'ask_password':
        user_state[user_id]['senha'] = incoming_msg
        dados_usuarios = carregar_dados_usuarios()
        numero = user_state[user_id]['numero']
        senha = user_state[user_id]['senha']
        idioma = user_state[user_id]['lang']  # Garantir que 'idioma' esteja definida
        nivel_acesso = validar_usuario(numero, senha, dados_usuarios)
        if nivel_acesso is not None:
            user_state[user_id]['nivel_acesso'] = nivel_acesso
            user_state[user_id]['step'] = 'main'
            response_text = ("Acesso concedido! Por favor, escolha uma das seguintes opções:\n1. Cardápio\n2. RH\n3. Eventos\n4. Procedimentos" 
                             if idioma == 'pt' else 
                             "Access granted! Please choose one of the following options:\n1. Menu\n2. HR\n3. Events\n4. Procedures")
        else:
            response_text = "Número de matrícula ou senha inválidos. Tente novamente." if idioma == 'pt' else "Invalid registration number or password. Please try again."
            user_state[user_id]['step'] = 'ask_credentials'
    else:
        idioma = user_state[user_id]['lang']
        nivel_acesso = user_state[user_id].get('nivel_acesso', 1)
        if incoming_msg.lower() == '1' and nivel_acesso in [2, 3]:
            response_text = "Encaminhando para o assistente de cardápio..." if idioma == 'pt' else "Forwarding to the menu assistant..."
        elif incoming_msg.lower() == '2' and nivel_acesso in [2, 3]:
            response_text = "Encaminhando para o assistente de RH..." if idioma == 'pt' else "Forwarding to the HR assistant..."
        elif incoming_msg.lower() == '3' and nivel_acesso == 3:
            response_text = "Encaminhando para o assistente de eventos..." if idioma == 'pt' else "Forwarding to the events assistant..."
        elif incoming_msg.lower() == '4' and nivel_acesso == 3:
            response_text = "Encaminhando para o assistente de procedimentos..." if idioma == 'pt' else "Forwarding to the procedures assistant..."
        else:
            response_text = get_openai_response(incoming_msg, lang=idioma)  # Chame a função para obter a resposta da OpenAI

    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
