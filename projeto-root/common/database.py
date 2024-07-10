import pandas as pd

def carregar_dados_usuarios():
    # Função para carregar dados dos usuários da planilha LibreOffice (ODS)
    caminho_arquivo = '/home/wesley/mvp-hotel/projeto-root/common/dados_usuarios.ods'
    # Ler as colunas como strings
    dados = pd.read_excel(caminho_arquivo, engine='odf', usecols=['NOME', 'NUM', 'SENHA', 'NÍVEL DE ACESSO'], dtype={'NUM': str, 'SENHA': str})
    # Remover linhas que contenham valores NaN
    dados = dados.dropna(subset=['NUM', 'SENHA'])
    return dados
