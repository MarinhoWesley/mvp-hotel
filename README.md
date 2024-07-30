# Meu Projeto

## Descrição do Projeto em Português

Este projeto implementa um chatbot baseado em WhatsApp para auxiliar na gestão interna de um hotel. O chatbot é capaz de identificar o idioma do usuário, validar suas credenciais e direcioná-lo para diferentes assistentes conforme seu nível de acesso. Utiliza a API do OpenAI para fornecer respostas inteligentes e a API do Twilio para enviar e receber mensagens via WhatsApp.

### Funcionalidades

- **Identificação de Idioma**: Detecta automaticamente o idioma da mensagem recebida (português ou inglês).
- **Validação de Usuário**: Verifica as credenciais do usuário (número de matrícula e senha) para determinar seu nível de acesso.
- **Assistentes Modulares**: Direciona o usuário para diferentes assistentes (Cardápio, RH, Eventos, Procedimentos) com base no nível de acesso.
- **Resposta Inteligente**: Utiliza a API do OpenAI para gerar respostas contextuais e úteis.
- **Integração com WhatsApp**: Utiliza a API do Twilio para comunicação via WhatsApp.

### Estrutura do Projeto

- **assistente_central**: Contém o código principal do chatbot que gerencia a identificação do idioma, validação de usuário e direcionamento para assistentes específicos.
- **assistente_cardapio, assistente_rh, assistente_eventos, assistente_procedimentos**: Contém códigos específicos para cada assistente.
- **common**: Contém configurações comuns, utilitários e a função de carregamento de dados dos usuários.
- **api**: Define as rotas da API Flask.
- **tests**: Contém testes para cada módulo do projeto.
- **scripts**: Scripts para deploy e configuração do ambiente.

## Descrição do Projeto em Inglês

This project implements a WhatsApp-based chatbot to assist with the internal management of a hotel. The chatbot can identify the user's language, validate their credentials, and direct them to different assistants based on their access level. It uses the OpenAI API to provide intelligent responses and the Twilio API to send and receive messages via WhatsApp.

### Features

- **Language Identification**: Automatically detects the language of the incoming message (Portuguese or English).
- **User Validation**: Verifies user credentials (registration number and password) to determine their access level.
- **Modular Assistants**: Directs the user to different assistants (Menu, HR, Events, Procedures) based on access level.
- **Intelligent Response**: Utilizes the OpenAI API to generate contextual and useful responses.
- **WhatsApp Integration**: Uses the Twilio API for communication via WhatsApp.

### Project Structure

- **assistente_central**: Contains the main chatbot code that manages language identification, user validation, and routing to specific assistants.
- **assistente_cardapio, assistente_rh, assistente_eventos, assistente_procedimentos**: Contains specific code for each assistant.
- **common**: Contains common configurations, utilities, and the function for loading user data.
- **api**: Defines the Flask API routes.
- **tests**: Contains tests for each module of the project.
- **scripts**: Scripts for deployment and environment setup.

## Como Usar / How to Use

### Pré-requisitos / Prerequisites

- Python 3.10 ou superior / Python 3.10 or higher
- Conta na OpenAI e Twilio / OpenAI and Twilio account

### Instalação / Installation

Clone o repositório e siga os passos abaixo:

```sh
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure as variáveis de ambiente criando um arquivo `.env` na raiz do projeto e adicionando suas chaves de API:
echo "OPENAI_API_KEY=your_openai_api_key" >> .env
echo "TWILIO_ACCOUNT_SID=your_twilio_account_sid" >> .env
echo "TWILIO_AUTH_TOKEN=your_twilio_auth_token" >> .env

# Execute o servidor Flask:
flask run

### Agora você pode interagir com o chatbot via WhatsApp! / Now you can interact with the chatbot via WhatsApp!

