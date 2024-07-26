import os
import sys

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import sys
import requests
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from common.database import carregar_dados_usuarios
from assistente_rh.rh import verificar_dias_ferias
from langdetect import detect, LangDetectException

# Configurar o logging para exibir apenas mensagens de aviso ou superiores
logging.basicConfig(level=logging.WARNING)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Acessar o token da API Zapster e instance_id
zapster_api_token = os.getenv('ZAPSTER_API_TOKEN')
zapster_base_url = 'https://new-api.zapsterapi.com'
zapster_instance_id = os.getenv('ZAPSTER_INSTANCE_ID')  # Certifique-se de que este é o ID correto e ativo

app = Flask(__name__)

user_state = {}

# Função para identificar o idioma da mensagem
def identificar_idioma(mensagem):
    saudacoes_pt = ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'ola']
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
        return usuario.iloc[0]['NOME'], usuario.iloc[0]['NÍVEL DE ACESSO']
    return None, None

# Função para gerar opções baseadas no nível de acesso
def gerar_opcoes(nivel_acesso, idioma):
    opcoes = []
    if nivel_acesso >= 1:
        opcoes.append("1. Cardápio" if idioma == 'pt' else "1. Menu")
    if nivel_acesso >= 2:
        opcoes.append("2. RH" if idioma == 'pt' else "2. HR")
    if nivel_acesso >= 3:
        opcoes.append("3. Eventos" if idioma == 'pt' else "3. Events")
        opcoes.append("4. Procedimentos" if idioma == 'pt' else "4. Procedures")
    return opcoes

# Função para enviar mensagens usando Zapster API
def enviar_mensagem(destinatario, mensagem):
    url = f"{zapster_base_url}/v1/wa/messages"  # Endpoint correto conforme documentação
    headers = {
        'Authorization': f'Bearer {zapster_api_token}',
        'Content-Type': 'application/json',
        'X-Instance-ID': zapster_instance_id  # Usando o cabeçalho HTTP para especificar a instância
    }
    data = {
        'recipient': destinatario,
        'text': mensagem
    }
    response = requests.post(url, headers=headers, json=data)
    
    # Logar o status da resposta e o conteúdo
    logging.warning(f"Status Code: {response.status_code}")
    logging.warning(f"Response Text: {response.text}")
    
    try:
        return response.json()
    except ValueError as e:
        logging.error("JSONDecodeError: Não foi possível decodificar a resposta JSON")
        logging.error(f"Response content: {response.text}")
        return None

# Endpoint principal para receber mensagens
@app.route('/webhook', methods=['POST'])
def webhook():
    # Logar o corpo da requisição
    logging.warning(f"Request JSON: {request.json}")
    
    # Ajuste para extrair os campos corretos
    data = request.json.get('data', {})
    incoming_msg = data.get('content', {}).get('text', '').strip().lower()
    user_id = data.get('sender', {}).get('id', '').strip()

    logging.warning(f"Incoming message: {incoming_msg}")
    logging.warning(f"User ID: {user_id}")

    # Reiniciar a conversa se o comando for "new"
    if incoming_msg == 'new':
        if user_id in user_state:
            del user_state[user_id]
        response_text = "Conversa reiniciada. Por favor, forneça seu número de matrícula." if identificar_idioma(incoming_msg) == 'pt' else "Conversation restarted. Please provide your registration number."
    elif user_id not in user_state:
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
        idioma = user_state[user_id]['lang']
        nome, nivel_acesso = validar_usuario(numero, senha, dados_usuarios)
        if nivel_acesso is not None:
            user_state[user_id]['nome'] = nome
            user_state[user_id]['nivel_acesso'] = nivel_acesso
            user_state[user_id]['step'] = 'main'
            response_text = (f"Acesso concedido! Olá {nome}! Por favor, escolha uma das seguintes opções:\n1. Cardápio\n2. RH\n3. Eventos\n4. Procedimentos\nDigite 'menu' a qualquer momento para voltar ao menu principal." 
                             if idioma == 'pt' else 
                             f"Access granted! Hello {nome}! Please choose one of the following options:\n1. Menu\n2. HR\n3. Events\n4. Procedures\nType 'menu' at any time to return to the main menu.")
        else:
            response_text = "Número de matrícula ou senha inválidos. Tente novamente." if idioma == 'pt' else "Invalid registration number or password. Please try again."
            user_state[user_id]['step'] = 'ask_credentials'
    else:
        idioma = user_state[user_id]['lang']
        nivel_acesso = user_state[user_id].get('nivel_acesso', 1)
        if incoming_msg == 'menu':
            response_text = (f"Acesso concedido! Olá {user_state[user_id]['nome']}! Por favor, escolha uma das seguintes opções:\n1. Cardápio\n2. RH\n3. Eventos\n4. Procedimentos\nDigite 'menu' a qualquer momento para voltar ao menu principal." 
                             if idioma == 'pt' else 
                             f"Access granted! Hello {user_state[user_id]['nome']}! Please choose one of the following options:\n1. Menu\n2. HR\n3. Events\n4. Procedures\nType 'menu' at any time to return to the main menu.")
            user_state[user_id]['step'] = 'main'
        elif incoming_msg == '1' and nivel_acesso >= 1:
            response_text = "Encaminhando para o assistente de cardápio..." if idioma == 'pt' else "Forwarding to the menu assistant..."
        elif incoming_msg == '2' and nivel_acesso >= 1:
            if nivel_acesso == 3:
                response_text = "Você está no assistente de RH. Digite o número de matrícula do funcionário que deseja consultar ou digite 'menu' para voltar ao menu central." if idioma == 'pt' else "You are in the HR assistant. Enter the registration number of the employee you want to consult or type 'menu' to return to the main menu."
                user_state[user_id]['step'] = 'rh_consulta'
            else:
                nome = user_state[user_id]['nome']
                response_text = verificar_dias_ferias(nome, None, idioma)  # Passar o idioma
        elif incoming_msg == '3' and nivel_acesso >= 3:
            response_text = "Encaminhando para o assistente de eventos..." if idioma == 'pt' else "Forwarding to the events assistant..."
        elif incoming_msg == '4' and nivel_acesso >= 3:
            response_text = "Encaminhando para o assistente de procedimentos..." if idioma == 'pt' else "Forwarding to the procedures assistant..."
        elif user_state[user_id]['step'] == 'rh_consulta':
            if incoming_msg == 'menu':
                response_text = (f"Acesso concedido! Olá {user_state[user_id]['nome']}! Por favor, escolha uma das seguintes opções:\n1. Cardápio\n2. RH\n3. Eventos\n4. Procedimentos\nDigite 'menu' a qualquer momento para voltar ao menu principal." 
                                 if idioma == 'pt' else 
                                 f"Access granted! Hello {user_state[user_id]['nome']}! Please choose one of the following options:\n1. Menu\n2. HR\n3. Events\n4. Procedures\nType 'menu' at any time to return to the main menu.")
                user_state[user_id]['step'] = 'main'
            else:
                response_text = verificar_dias_ferias(user_state[user_id]['nome'], incoming_msg, idioma)  # Passar o idioma
        else:
            response_text = "Opção inválida ou acesso não permitido. Digite 'menu' para retornar ao menu principal." if idioma == 'pt' else "Invalid option or access not allowed. Type 'menu' to return to the main menu."

    enviar_mensagem(user_id, response_text)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
