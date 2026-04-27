import os
from fastapi import FastAPI, Request
import requests
from google import genai  # Importando a nova biblioteca oficial

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Inicializando o cliente da IA
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None

def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Erro: Credenciais do Telegram não configuradas no .env")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"❌ Erro no Telegram ({response.status_code}): {response.text}")
    else:
        print("✅ Mensagem enviada com sucesso ao Telegram!")

def analisar_com_ia(dados_alerta):
    if not client:
        return "⚠️ Alerta recebido, mas a IA não está configurada (Falta API Key no .env)."
    
    prompt = f"""
    Você é um analista de segurança atuando em um SOC. 
    Analise o seguinte alerta de intrusão capturado por um honeypot Cowrie e gerado pelo Grafana:
    
    {dados_alerta}
    
    Forneça um relatório muito curto, em português, ideal para ler rápido no celular via Telegram contendo:
    1. Resumo do Ataque (o que o invasor fez ou tentou fazer)
    2. Nível de Ameaça (Baixo, Médio, Alto)
    3. Mitigação Recomendada (o que a equipe de infraestrutura deve fazer)
    
    Seja direto, profissional e use emojis para facilitar a leitura. Não inclua código JSON na resposta.
    """
    
    try:
        # Usando a sintaxe moderna do novo SDK
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ Erro ao processar análise com a IA: {e}"

@app.post("/webhook")
async def recebe_alerta(request: Request):
    dados = await request.json()
    status = dados.get("status", "unknown")
    
    if status == "firing":
        print("Novo ataque detectado! Iniciando análise com IA via SDK moderno...")
        
        # alertas = dados.get("alerts", [])
        # detalhes_do_ataque = alertas[0] if alertas else dados
        
        # relatorio_ia = analisar_com_ia(detalhes_do_ataque)
        
        alertas = dados.get("alerts", [])
        detalhes_do_ataque = alertas[0] if alertas else dados
        
        # Converte para string e corta nos primeiros 2000 caracteres
        texto_do_ataque = str(detalhes_do_ataque)[:2000]
        
        relatorio_ia = analisar_com_ia(texto_do_ataque)
        
        mensagem_final = f"🚨 *NOVO ATAQUE DETECTADO NO HONEYPOT*\n\n{relatorio_ia}"
        enviar_telegram(mensagem_final)
        
        return {"status": "Processado com IA e Enviado ao Telegram"}
    
    else: 
        print(f"Alerta recebido com status: {status}. Ignorando.")
        return {"status": "Ignorado"}