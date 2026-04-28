import streamlit as st
import requests
import pandas as pd

# URL da sua FastAPI (ajuste a porta se necessário, geralmente o Uvicorn roda na 8000)
API_URL = "http://alerts-api:8000/alerts"

# Configuração visual da página
st.set_page_config(
    page_title="SOC - Threat Intelligence", 
    layout="wide", 
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para deixar com "cara de hacker/SOC"
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .titulo { color: #00FFAA; font-family: 'Courier New', Courier, monospace; }
    .ai-report { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #00FFAA; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🛡️ Portal de Threat Intelligence - IoT</h1>", unsafe_allow_html=True)
st.markdown("*Monitoramento Ativo de Honeypots Embarcados (Cowrie)*")
st.divider()

# Função para buscar dados do Backend
def fetch_alerts():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Busca os dados
data = fetch_alerts()

# Cria as métricas do topo
col1, col2, col3 = st.columns(3)

if data is not None:
    alertas = data.get("alerts", [])
    total_alertas = data.get("total", 0)
    
    col1.metric("Status da API", "Online 🟢", "Conectado")
    col2.metric("Total de Alertas Capturados", total_alertas, "Sessão Atual")
    col3.metric("Integração Telegram & IA", "Ativa 🤖", "Gemini 2.0")
    
    st.divider()
    st.subheader("🚨 Últimas Intrusões Detectadas")
    
    if total_alertas == 0:
        st.info("Nenhum ataque detectado ainda. Aguardando o Grafana disparar alertas de webhook...")
    else:
        # Mostra cada alerta de forma interativa
        for i, alerta in enumerate(alertas):
            with st.expander(f"⚠️ Alerta {i+1} | Detectado em: {alerta['timestamp']}"):
                col_ia, col_raw = st.columns([2, 1])
                
                with col_ia:
                    st.markdown("### 🤖 Análise da IA (Gemini 2.0)")
                    st.markdown(f"<div class='ai-report'>{alerta['ai_analysis']}</div>", unsafe_allow_html=True)
                
                with col_raw:
                    st.markdown("### 🛠️ Dados Brutos (JSON)")
                    st.json(alerta['raw_data'])

else:
    col1.metric("Status da API", "Offline 🔴", "-")
    col2.metric("Total de Alertas", "-", "-")
    st.error("Não foi possível conectar à API de alertas. Certifique-se de que o Uvicorn/Docker do backend está rodando na porta 8000.")

st.divider()
st.subheader("📊 Observabilidade em Tempo Real")
st.markdown("Para visualizar os gráficos avançados e mapas de calor, acesse o painel de métricas.")
# Botão para redirecionar para o seu Grafana
st.link_button("Abrir Dashboard Completo no Grafana", "http://localhost:3000")