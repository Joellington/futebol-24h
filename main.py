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
PV_LINK = "@joellington1"

# CONFIGURAÇÃO DAS CASAS COM AS FOTOS QUE VOCÊ ENVIOU
CASAS = [
    {"n": "THUNDER", "l": "https://go.thunder.partners/visit/?bta=37612&nci=5734&campaign=WELCOME", "img": "https://i.postimg.cc/fVMd5FHh/zeus.png", "txt": "⚡ Odd turbinada na Thunder!"},
    {"n": "WILD", "l": "https://wildpartners.app/aygxryvmo", "img": "https://i.postimg.cc/jLHNHK4w/cassino-luxo.png", "txt": "🎰 Bônus de Cassino e Esportes na Wild!"},
    {"n": "1XBIT", "l": "https://refpa04636.pro/L?tag=d_4461890m_99582c_&site=4461890&ad=99582", "img": "https://i.postimg.cc/mPT9Vqmn/crypto-elite.png", "txt": "₿ Elite das Apostas com Cripto!"},
    {"n": "DB BET", "l": "https://refpa96317.com/L?tag=d_5308638m_11213c_&site=5308638&ad=11213", "img": "https://i.postimg.cc/pmPjk7s3/esportes.png", "txt": "🟢 DB BET: Saque via PIX mais rápido do mercado!"},
    {"n": "PARIPESA", "l": "https://combodef.com/L?tag=d_5573724m_45569c_&site=5573724&ad=45569", "img": "https://i.postimg.cc/3k3G96L5/paripesa.png", "txt": "⚠️ Use o código 'Jogo' na Paripesa para BÔNUS! 🎁"}
]

# ================= BIBLIOTECA HUMANIZADA (GÍRIAS E ANÁLISES) =================
ANALISES = [
    "Gráfico de pressão tá batendo no teto! O gol tá maduro.", "O time da casa tá amassando, a zebra não passa do meio campo.",
    "Achei um desajuste absurdo nessa odd aqui, vamos aproveitar!", "Leitura de jogo feita: os cantos vão sair em sequência agora.",
    "Sniper ativado! Esse mercado de cartões tá muito lucrativo.", "O favorito tá com sangue nos olhos, não sai da área adversária.",
    "Estatísticas de elite detectadas pelo nosso algoritmo.", "Jogo muito aberto, ideal para nossa estratégia de gols.",
    "Análise pré-live confirmada pelo desempenho ao vivo. É o ouro!", "A casa de apostas vacilou nessa linha, vamos entrar forte."
]

CHAMADAS = [
    "Vou com 2 unidades aqui, gestão de banca sempre!", "Quem tá no lucro comigo? Bora pra mais uma!",
    "Entrem rápido, essa odd vai despencar!", "Confiem na leitura, o mestre tá inspirado hoje.",
    "Preparem o grito de Green! Essa é muito forte.", "Bora buscar o café da manhã com essa entrada.",
    "Acompanhem o movimento, valor puro nesse mercado.", "Sem medo! A análise técnica é impecável aqui."
]

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
def home(): return "Robô Ativo e Lucrando!"
def run_site(): app.run(host='0.0.0.0', port=8080)

# ================= O CÉREBRO DO ROBÔ =================
def monitorar_tudo():
    # Inicia banco de dados para lucro/perda
    conn = sqlite3.connect('master.db')
    conn.execute('CREATE TABLE IF NOT EXISTS sinais (id_j TEXT PRIMARY KEY, status TEXT, stake REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS banca (id INTEGER PRIMARY KEY, lucro REAL, g INTEGER, r INTEGER)')
    if not conn.execute('SELECT * FROM banca').fetchone(): conn.execute('INSERT INTO banca VALUES (1, 0, 0, 0)')
    conn.commit()
    conn.close()

    while True:
        try:
            # Seleciona Esporte e Mercado aleatório para diversificar
            esporte = random.choice(["FUTEBOL", "NBA", "FIFA", "CS:GO", "VOLEI"])
            casa = random.choice(CASAS)
            
            # Busca jogos reais de futebol ou basquete
            jogos_reais = get_api_data("fut" if esporte in ["FUTEBOL", "FIFA"] else "bas", "fixtures?live=all")
            
            if jogos_reais:
                j = random.choice(jogos_reais)
                t1, t2 = j['teams']['home']['name'], j['teams']['away']['name']
                id_j = f"GAME_{j.get('id', random.randint(1000,9999))}"
                
                # Define o mercado baseado no esporte
                mercado = random.choice(["Over 1.5 Gols", "Escanteios HT", "Mais de 3.5 Cartões", "Vencer Partida"])
                if esporte == "NBA": mercado = "Over Pontos Q4"
                if esporte == "FIFA": mercado = "Mais de 2.5 Gols (10 min)"
                if esporte == "CS:GO": mercado = "Vencedor Mapa 2"

                stake = random.choice([1, 2, 3])
                msg = (
                    f"🎯 **NOVA ENTRADA: {esporte}**\n\n"
                    f"🏟 **{t1} x {t2}**\n"
                    f"✅ **Entrada:** {mercado}\n"
                    f"💰 **Gestão:** {stake} Unidades\n\n"
                    f"📝 **Análise:** {random.choice(ANALISES)}\n"
                    f"🚀 {random.choice(CHAMADAS)}"
                )
                
                # Envia com a foto da casa correspondente
                footer = f"\n\n{casa['txt']}\n🔗 [APOSTE AQUI COM BÔNUS]({casa['l']})"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                             data={'chat_id': CHAT_ID, 'photo': casa['img'], 'caption': msg + footer, 'parse_mode': 'Markdown'})
                
                # Salva sinal como pendente
                conn = sqlite3.connect('master.db')
                conn.execute('INSERT OR IGNORE INTO sinais VALUES (?,?,?)', (id_j, 'PENDENTE', stake))
                conn.commit()
                conn.close()

            # Lógica de Green/Red (Simula resultado após 15 min)
            time.sleep(900) # Espera 15 min para o próximo sinal ou resultado
            
            # Manda um feedback de resultado aleatório para movimentar
            feedback = random.choice([
                "✅✅ **GREEN! MAIS UM PRA CONTA!**",
                "✅ **TÁ LÁ! O LUCRO CAIU!**",
                "❌ Essa não bateu. Mantemos a gestão de banca.",
                "✅ **GREEN CONFIRMADO!** Quem seguiu lucrou!"
            ])
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': feedback, 'parse_mode': 'Markdown'})
            
            # Relatório de Lucro a cada 5 sinais
            if random.randint(1, 5) == 3:
                relat = "📊 **RELATÓRIO DE HOJE:**\n✅ Greens: 12\n❌ Reds: 2\n💰 Lucro: +8.5 Units\n\nSeguimos a meta!"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': relat, 'parse_mode': 'Markdown'})

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == "__main__":
    Thread(target=run_site).start()
    monitorar_tudo()
