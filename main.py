import requests
import time
import sqlite3
import random
from datetime import datetime
from flask import Flask
from threading import Thread

# ================= CONFIGURAÇÕES MASTER =================
TOKEN = '7144823144:AAGbrTI2a-XdsyHrpsAGpCQYdGHR30Cxd-g'
CHAT_ID = '@jogorapidoo'
API_KEY = '62d36a176d2e9b4ea1227525462dde7c'
PV_LINK = "joellington1" # Seu usuário configurado aqui

# CONFIGURAÇÃO DAS CASAS COM SEUS LINKS DE FOTOS REAIS
CASAS = [
    {"n": "THUNDER", "l": "https://go.thunder.partners/visit/?bta=37612&nci=5734&campaign=WELCOME", "img": "https://i.postimg.cc/fVMd5FHh/zeus.png", "txt": "⚡ Oportunidade na Thunder! Odds no teto!"},
    {"n": "WILD", "l": "https://wildpartners.app/aygxryvmo", "img": "https://i.postimg.cc/jLHNHK4w/cassino-luxo.png", "txt": "🎰 A Wild está pagando muito nesse mercado!"},
    {"n": "1XBIT", "l": "https://refpa04636.pro/L?tag=d_4461890m_99582c_&site=4461890&ad=99582", "img": "https://i.postimg.cc/mPT9Vqmn/crypto-elite.png", "txt": "₿ Elite das Apostas! Entre pela 1xBit!"},
    {"n": "DB BET", "l": "https://refpa96317.com/L?tag=d_5308638m_11213c_&site=5308638&ad=11213", "img": "https://i.postimg.cc/pmPjk7s3/esportes.png", "txt": "🟢 DB BET: Saque instantâneo liberado!"},
    {"n": "PARIPESA", "l": "https://combodef.com/L?tag=d_5573724m_45569c_&site=5573724&ad=45569", "img": "https://i.postimg.cc/3k3G96L5/paripesa.png", "txt": "⚠️ Use o código 'Jogo' na Paripesa para BÔNUS! 🎁"}
]

# FRASES PARA HUMANIZAÇÃO
ANALISES = [
    "O gráfico de pressão tá explodindo! O gol tá maduro.", "Estatísticas indicam tendência forte de cantos agora.",
    "O favorito tá amassando, a zebra não passa do meio de campo.", "Radar ativado! Vi valor absurdo nessa entrada.",
    "Mercado de cartões tá no ponto, o juiz é rigoroso.", "Análise técnica feita: probabilidade de 94% aqui.",
    "A odd tá desajustada, vamos aproveitar esse erro da casa!", "Acabei de filtrar esse jogo, valor puro!"
]

# ================= FUNÇÕES DE ENVIO (SISTEMA DE FOTOS) =================
def enviar_telegram(msg, casa_obj):
    url = f"https://api.telegram.org/bot{TOKEN}/"
    footer = f"\n\n{casa_obj['txt']}\n🚀 [APOSTE AQUI]({casa_obj['l']})\n📩 Dúvidas no PV: https://t.me/{PV_LINK}"
    
    try:
        # Tenta enviar com foto
        res = requests.post(url + "sendPhoto", data={
            'chat_id': CHAT_ID, 
            'photo': casa_obj['img'], 
            'caption': msg + footer, 
            'parse_mode': 'Markdown'
        })
        # Se falhar a foto, envia só texto para não perder a entrada
        if res.status_code != 200:
            requests.post(url + "sendMessage", data={
                'chat_id': CHAT_ID, 
                'text': msg + footer, 
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            })
    except: pass

# ================= MOTOR DE DADOS =================
def get_api_data(sport, end):
    hosts = {"fut": "v3.football.api-sports.io", "bas": "v3.basketball.api-sports.io"}
    h = {'x-rapidapi-host': hosts.get(sport, hosts['fut']), 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(f"https://{hosts.get(sport, hosts['fut'])}/{end}", headers=h, timeout=15)
        return r.json().get('response', [])
    except: return []

app = Flask('')
@app.route('/')
def home(): return "Robô Ativo com Fotos e PV Corrigido!"
def run_site(): app.run(host='0.0.0.0', port=8080)

# ================= LOOP PRINCIPAL =================
def monitorar():
    while True:
        try:
            casa = random.choice(CASAS)
            # Tenta buscar futebol ao vivo
            jogos = get_api_data("fut", "fixtures?live=all")
            
            if jogos:
                j = random.choice(jogos)
                t1, t2 = j['teams']['home']['name'], j['teams']['away']['name']
                
                # Sorteia mercados reais
                mercados = ["Over 1.5 Gols", "Mais de 8.5 Escanteios", "Ambas Marcam", "Mais de 3.5 Cartões"]
                escolha = random.choice(mercados)
                
                msg = (
                    f"⚽ **ENTRADA REAL CONFIRMADA**\n\n"
                    f"🏟 **{t1} x {t2}**\n"
                    f"🎯 **Entrada:** {escolha}\n"
                    f"💰 **Sugestão:** {random.randint(1,3)}% da banca\n\n"
                    f"💡 {random.choice(ANALISES)}"
                )
                enviar_telegram(msg, casa)
            
            # Mensagens de interação/E-sports simuladas caso não tenha jogo real bom
            elif random.randint(1, 3) == 2:
                msg_interacao = random.choice([
                    "🎮 **FIFA / ESPORTS:** Tô filtrando umas partidas aqui, fiquem ligados!",
                    "🏀 **NBA:** Rodada de hoje tá prometendo, jaja mando as brabas!",
                    "🔥 O canal tá on! Quem tá lucrando manda o print no PV!"
                ])
                enviar_telegram(msg_interacao, casa)

            # Resultados aleatórios para manter o canal vivo
            if random.randint(1, 4) == 2:
                res_msg = random.choice(["✅ GREEN! Lucro no bolso!", "✅✅ TÁ LÁ! Mais um green!", "❌ Red. Seguimos a gestão."])
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': res_msg})

            time.sleep(random.randint(400, 800)) # Intervalo humano entre 6 e 13 minutos
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == "__main__":
    Thread(target=run_site).start()
    monitorar()
