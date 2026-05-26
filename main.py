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

# Configuração das Casas com suas Imagens (Substitua pelos links reais das suas fotos)
CASAS = [
    {"n": "THUNDER", "l": "https://go.thunder.partners/visit/?bta=37612&nci=5734", "img": "https://i.postimg.cc/zeus_thunder.jpg", "cor": "Amarela"},
    {"n": "WILD", "l": "https://wildpartners.app/aygxryvmo", "img": "https://i.postimg.cc/wild_casino.jpg", "cor": "Dourada"},
    {"n": "1XBIT", "l": "https://refpa04636.pro/L?tag=d_4461890m_99582c_", "img": "https://i.postimg.cc/1xbit_green.jpg", "cor": "Verde"},
    {"n": "DB BET", "l": "https://refpa96317.com/L?tag=d_5308638m_11213c_", "img": "https://i.postimg.cc/dbbet_green.jpg", "cor": "Verde"},
    {"n": "PARIPESA", "l": "https://combodef.com/L?tag=d_5573724m_45569c_&site=5573724&ad=45569", "img": "https://i.postimg.cc/paripesa_blue.jpg", "cor": "Azul"}
]

# ================= BIBLIOTECA HUMANIZADA (VARIEDADE TOTAL) =================
ANALISES = [
    "O gráfico de pressão tá explodindo aqui!", "O time visitante tá todo recuado, o gol tá maduro.",
    "Estatísticas de elite detectadas pelo algoritmo.", "Acabei de receber um insider sobre esse confronto.",
    "Valor absurdo nessa odd, a casa de apostas vacilou feio.", "O favorito tá amassando, não sai desse campo de ataque.",
    "O sniper da equipe de e-sports tá num dia inspirado.", "Muitas faltas e jogo parado, o mercado de cartões é o ouro aqui.",
    "O histórico desse juiz favorece muito nossa entrada.", "Jogo de 'vida ou morte' pra eles, vão se expor no contra-ataque."
]

CHAMADAS = [
    "Vou entrar com 2 unidades aqui sem medo!", "Gestão conservadora, mas a entrada é ótima.",
    "Quem vem comigo nessa? O lucro tá batendo na porta.", "Bora buscar o café da manhã!",
    "Preparem as bancas, o sinal é forte.", "Confiem no processo, a análise foi minuciosa.",
    "Entrem rápido antes que a odd caia!", "Vou pesado nessa, sinto cheiro de green."
]

# ================= MOTOR DE MERCADOS =================
def gerar_entrada_real(esporte):
    mercados = {
        "futebol": ["Mais de 1.5 Gols", "Mais de 8.5 Escanteios", "Ambas Marcam", "Handicap -1.0", "Mais de 3.5 Cartões"],
        "basquete": ["Over Pontos no Q3", "Vencedor Partida (ML)", "Handicap de Pontos", "Total de Assistências"],
        "esports": ["Vencedor do Mapa 1", "Total de Rounds Over", "Handicap de Mapas", "First Blood (Primeiro abate)"],
        "volei": ["Mais de 45.5 Pontos no Set", "Vencedor do Jogo", "Handicap de Sets"],
        "fifa": ["Mais de 2.5 Gols (10 min)", "Vencedor da Partida", "Over 0.5 Gols HT"]
    }
    lista = mercados.get(esporte, ["Over Gols/Pontos"])
    return random.choice(lista)

# ================= FUNÇÃO DE ENVIO E BANCO =================
def enviar_sinal(msg, casa, foto_casa):
    url = f"https://api.telegram.org/bot{TOKEN}/"
    footer = f"\n\n🎁 **BÔNUS NA {casa['n']}:** Use o código **'JOGO'**\n🔗 [CLIQUE AQUI PARA APOSTAR]({casa['l']})"
    
    try:
        payload = {'chat_id': CHAT_ID, 'photo': foto_casa, 'caption': msg + footer, 'parse_mode': 'Markdown'}
        requests.post(url + "sendPhoto", data=payload)
    except: pass

def log_banca(tipo, valor):
    conn = sqlite3.connect('master_stats.db')
    if tipo == "GREEN":
        conn.execute('UPDATE banca SET lucro_total = lucro_total + ?, greens = greens + 1 WHERE id=1', (valor,))
    else:
        conn.execute('UPDATE banca SET lucro_total = lucro_total - ?, reds = reds + 1 WHERE id=1', (valor,))
    conn.commit()
    conn.close()

# ================= O CÉREBRO DO ROBÔ (LOOP) =================
def monitorar_global():
    # Inicializa DB se não existir
    conn = sqlite3.connect('master_stats.db')
    conn.execute('CREATE TABLE IF NOT EXISTS sinais (id_j TEXT PRIMARY KEY, status TEXT, data TEXT, stake REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS banca (id INTEGER PRIMARY KEY, lucro_total REAL, greens INTEGER, reds INTEGER)')
    if not conn.execute('SELECT * FROM banca').fetchone():
        conn.execute('INSERT INTO banca VALUES (1, 0.0, 0, 0)')
    conn.commit()
    conn.close()

    while True:
        try:
            # 1. ESCOLHE O ESPORTE DO MOMENTO (Para dar variedade)
            esporte_da_rodada = random.choice(["futebol", "basquete", "volei", "esports", "fifa"])
            casa = random.choice(CASAS)
            
            # 2. BUSCA DADOS REAIS (Exemplo Futebol)
            jogos = get_api_data("fut" if esporte_da_rodada in ["futebol", "fifa"] else "bas", "fixtures?live=all")
            
            if not jogos: # Se não tiver jogo ao vivo, manda uma pré-análise
                time.sleep(60)
                continue

            j = random.choice(jogos) # Pega um jogo aleatório para não ser sempre o primeiro
            id_j = f"{esporte_da_rodada}_{j.get('id', random.randint(1,99999))}"

            conn = sqlite3.connect('master_stats.db')
            if not conn.execute('SELECT id_j FROM sinais WHERE id_j=?', (id_j,)).fetchone():
                t1 = j['teams']['home']['name']
                t2 = j['teams']['away']['name']
                entrada = gerar_entrada_real(esporte_da_rodada)
                stake = random.choice([1, 1.5, 2, 2.5, 3, 5])
                
                # Montagem da Mensagem Humanizada
                emoji = "⚽" if esporte_da_rodada == "futebol" else "🎮" if esporte_da_rodada == "esports" else "🏀"
                msg = (
                    f"{emoji} **NOVA OPORTUNIDADE: {esporte_da_rodada.upper()}**\n"
                    f"⚔️ **{t1} vs {t2}**\n\n"
                    f"📝 **Análise:** {random.choice(ANALISES)}\n"
                    f"🎯 **Entrada:** {entrada}\n"
                    f"💰 **Sugestão:** {stake}% da banca\n\n"
                    f"💡 {random.choice(CHAMADAS)}"
                )
                
                enviar_sinal(msg, casa, casa['img'])
                conn.execute('INSERT INTO sinais VALUES (?,?,?,?)', (id_j, 'PENDENTE', str(datetime.now()), stake))
                conn.commit()
            conn.close()

            # 3. FEEDBACK DE RESULTADOS (Verifica 1 sinal antigo por ciclo)
            if random.randint(1, 4) == 2:
                conn = sqlite3.connect('master_stats.db')
                antigo = conn.execute('SELECT id_j, stake FROM sinais WHERE status="PENDENTE" LIMIT 1').fetchone()
                if antigo:
                    if random.random() > 0.35: # 65% de taxa de acerto simulada
                        log_banca("GREEN", antigo[1] * 0.9)
                        msg_g = random.choice(["✅ CAIU O PIX! Green absurdo!", "✅ GREEN! O mestre não erra!", "✅ TÁ LÁ! Lucro no bolso família!"])
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': msg_g})
                    else:
                        log_banca("RED", antigo[1])
                        msg_r = random.choice(["❌ Essa não veio. O time entregou no final.", "❌ Red. Faz parte da gestão, sem pânico.", "❌ Não bateu. Vamos pra próxima com calma."])
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': msg_r})
                    conn.execute('UPDATE sinais SET status="FIM" WHERE id_j=?', (antigo[0],))
                conn.commit()
                conn.close()

            # 4. RELATÓRIO DE BANCA PERIÓDICO
            if random.randint(1, 20) == 10:
                conn = sqlite3.connect('master_stats.db')
                b = conn.execute('SELECT * FROM banca').fetchone()
                relat = f"📈 **RESUMO DA SESSÃO**\n\n✅ Greens: {b[2]}\n❌ Reds: {b[3]}\n💰 Lucro: {b[1]:.2f} units\n\nBora pra cima! 🚀"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': relat})
                conn.close()

            time.sleep(random.randint(300, 600)) # Pausa entre 5 e 10 min para parecer humano
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(30)

# (Mantenha as funções do Flask e requests API que já funcionam)
if __name__ == "__main__":
    Thread(target=run_site).start()
    monitorar_global()
