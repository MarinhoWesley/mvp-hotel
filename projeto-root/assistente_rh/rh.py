import pandas as pd

def carregar_dados_ferias():
    caminho_arquivo = '/home/wesley/mvp-hotel/projeto-root/common/ferias.ods'
    dados = pd.read_excel(caminho_arquivo, engine='odf', dtype={'NUM': str})
    return dados

def verificar_dias_ferias(nome, numero_consulta=None, idioma='pt'):
    dados_ferias = carregar_dados_ferias()
    
    if numero_consulta:
        dados_usuario = dados_ferias[dados_ferias['NUM'] == numero_consulta]
        if not dados_usuario.empty:
            nome_consulta = dados_usuario.iloc[0]['NOME']
            dias_ferias = dados_usuario.iloc[0]['DIAS']
            if idioma == 'pt':
                return f"O funcionário {nome_consulta} tem {dias_ferias} dias de férias."
            else:
                return f"The employee {nome_consulta} has {dias_ferias} vacation days."
        else:
            return "Número de matrícula não encontrado." if idioma == 'pt' else "Registration number not found."
    else:
        dados_usuario = dados_ferias[dados_ferias['NOME'] == nome]
        if not dados_usuario.empty:
            dias_ferias = dados_usuario.iloc[0]['DIAS']
            if idioma == 'pt':
                return f"Você possui {dias_ferias} dias de férias."
            else:
                return f"You have {dias_ferias} vacation days."
        else:
            return "Usuário não encontrado." if idioma == 'pt' else "User not found."
