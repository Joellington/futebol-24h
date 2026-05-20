import requests
import time
import sqlite3
import random
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# ================= CONFIGURAÇÕES MASTER =================
TOKEN = '7144823144:AAGbrTI2a-XdsyHrpsAGpCQYdGHR30Cxd-g'
CHAT_ID = '@jogorapidoo'
API_KEY = '62d36a176d2e9b4ea1227525462dde7c'
PV_LINK = "https://t.me/SEU_USUARIO_PV"

CASAS = [
    {"n": "THUNDER", "l": "https://go.thunder.partners/visit/?bta=37612&nci=5734&campaign=WELCOME"},
    {"n": "WILD", "l": "https://wildpartners.app/aygxryvmo"},
    {"n": "1XBIT", "l": "https://refpa04636.pro/L?tag=d_4461890m_99582c_&site=4461890&ad=99582"},
    {"n": "DB BET", "l": "https://refpa96317.com/L?tag=d_5308638m_11213c_&site=5308638&ad=11213"}
]

# ================= BANCO DE DADOS (ANTI-REPETIÇÃO) =================
def init_db():
    conn = sqlite3.connect('master_stats.db')
    conn.execute('CREATE TABLE IF NOT EXISTS sinais (id_j TEXT PRIMARY KEY, status TEXT, data TEXT)')
    conn.commit()
    conn.close()

# ================= MOTOR DE INTELIGÊNCIA DE TEXTO =================
def gerar_comentario(time_fav, time_zebra, esporte="futebol"):
    frases = [
        f"Vi aqui que o {time_fav} está amassando. Entrei forte!",
        f"O {time_fav} é muito favorito, mas o {time_zebra} tem uma escapada perigosa.",
        f"Achei uma oportunidade de ouro nesse jogo do {time_fav}.",
        f"O mercado de gols/pontos aqui está com valor. Vamos aproveitar!",
        f"Análise feita: o {time_fav} deve confirmar o favoritismo, mas vamos com gestão.",
        f"Essa entrada aqui é pra quem tem peito. Vamos pra cima!",
        f"Estatísticas de elite detectadas no confronto {time_fav} x {time_zebra}."
    ]
    return random.choice(frases)

# ================= FUNÇÕES DE ENVIO =================
def enviar_telegram(txt, foto=None):
    url = f"https://api.telegram.org/bot{TOKEN}/"
    try:
        casa = random.choice(CASAS)
        footer = f"\n\n🚀 [APOSTE NA {casa['n']} AQUI]({casa['l']})\n📩 Dúvidas no PV: {PV_LINK}"
        if foto:
            requests.post(url + "sendPhoto", data={'chat_id': CHAT_ID, 'photo': foto, 'caption': txt + footer, 'parse_mode': 'Markdown'})
        else:
            requests.post(url + "sendMessage", data={'chat_id': CHAT_ID, 'text': txt + footer, 'parse_mode': 'Markdown'})
    except: pass

# ================= MOTOR DE DADOS (MÚLTIPLOS ESPORTES) =================
def get_api_data(sport, end):
    hosts = {
        "fut": "v3.football.api-sports.io",
        "bas": "v3.basketball.api-sports.io"
    }
    h = {'x-rapidapi-host': hosts.get(sport, hosts['fut']), 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(f"https://{hosts.get(sport, hosts['fut'])}/{end}", headers=h, timeout=15)
        return r.json().get('response', [])
    except: return []

# ================= SITE PARA O RENDER NÃO DORMIR =================
app = Flask('')
@app.route('/')
def home(): return "Robô Omnisciente Ativo 24h"

def run_site(): app.run(host='0.0.0.0', port=8080)

# ================= LOOP PRINCIPAL (A MÁQUINA) =================
def monitorar_tudo():
    init_db()
    while True:
        try:
            # 1. ANALISA FUTEBOL AO VIVO (AGRESSIVO)
            jogos_fut = get_api_data("fut", "fixtures?live=all")
            for j in jogos_fut:
                id_j = f"FUT_{j['fixture']['id']}"
                conn = sqlite3.connect('master_stats.db')
                if not conn.execute('SELECT id_j FROM sinais WHERE id_j=?', (id_j,)).fetchone():
                    t1, t2 = j['teams']['home']['name'], j['teams']['away']['name']
                    msg = f"⚽ **FUTEBOL AO VIVO**\n🏟 {t1} x {t2}\n🎯 Entrada: Over Gols\n\n💡 {gerar_comentario(t1, t2)}"
                    enviar_telegram(msg, j['teams']['home']['logo'])
                    conn.execute('INSERT INTO sinais VALUES (?,?,?)', (id_j, 'PENDENTE', str(datetime.now())))
                    conn.commit()
                conn.close()

            # 2. ANALISA NBA/BASQUETE
            jogos_bas = get_api_data("bas", "games?live=all")
            for b in jogos_bas:
                id_b = f"BAS_{b['id']}"
                conn = sqlite3.connect('master_stats.db')
                if not conn.execute('SELECT id_j FROM sinais WHERE id_j=?', (id_b,)).fetchone():
                    t1, t2 = b['teams']['home']['name'], b['teams']['away']['name']
                    msg = f"🏀 **BASQUETE / NBA**\n🏀 {t1} x {t2}\n🎯 Entrada: Over Pontos\n\n💡 {gerar_comentario(t1, t2, 'basquete')}"
                    enviar_telegram(msg, b['teams']['home']['logo'])
                    conn.execute('INSERT INTO sinais VALUES (?,?,?)', (id_b, 'PENDENTE', str(datetime.now())))
                    conn.commit()
                conn.close()

            # 3. ANALISA PRÉ-JOGO (DICAS PARA AMANHÃ E HOJE TARDE)
            hoje = datetime.now().strftime("%Y-%m-%d")
            amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            for data_analise in [hoje, amanha]:
                pre_jogos = get_api_data("fut", f"fixtures?date={data_analise}")
                for p in pre_jogos[:10]: # Pega os 10 principais do dia
                    id_p = f"PRE_{p['fixture']['id']}"
                    conn = sqlite3.connect('master_stats.db')
                    if not conn.execute('SELECT id_j FROM sinais WHERE id_j=?', (id_p,)).fetchone():
                        t1, t2 = p['teams']['home']['name'], p['teams']['away']['name']
                        msg = f"💎 **DICA PRÉ-JOGO ({data_analise})**\n🏟 {t1} x {t2}\n🎯 Entrada: Vitória do Favorito\n\n💡 Analisei esse jogo horas antes e a zebra não tem chance aqui."
                        enviar_telegram(msg, p['teams']['home']['logo'])
                        conn.execute('INSERT INTO sinais VALUES (?,?,?)', (id_p, 'ENVIADO', str(datetime.now())))
                        conn.commit()
                    conn.close()

            # 4. MENSAGENS DE RESULTADO (GREEN/RED AUTOMÁTICO)
            # (Aqui simulamos o feedback para o canal ter movimento)
            if random.randint(1, 5) == 3:
                resultado = random.choice([
                    "✅ GREEN! VAMOS LÁ! O lucro entrou!",
                    "✅✅ MAIS UM GREEN! O mestre avisou!",
                    "❌ Red pessoal. Essa foi ruim, o time não rendeu.",
                    "❌ Pegamos Red aqui. Faz parte da gestão, vamos recuperar!"
                ])
                enviar_telegram(resultado)

            # 5. E-SPORTS / VÔLEI (INTERAÇÃO)
            if random.randint(1, 10) == 7:
                msg_extra = random.choice([
                    "🎮 **VALORANT / CS:GO:** Tô de olho numas partidas aqui, jaja mando algo!",
                    "🏐 **VÔLEI:** Alguém operando vôlei hoje? As ligas europeias tão pagando muito!",
                    "🔥 O canal tá bombando! Mandem o print dos lucros no PV!"
                ])
                enviar_telegram(msg_extra)

            print("♻️ Ciclo de análise global completo.")
            time.sleep(300) # Varre tudo a cada 5 minutos
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == "__main__":
    Thread(target=run_site).start()
    monitorar_tudo()
