import telebot
from telebot import types
import time
import random
import os
import json
import requests
from datetime import datetime
from flask import Flask
import threading

# 1. SERVIDOR FLASK
app = Flask('')
@app.route('/')
def home():
    return "🤖 Setup da Estrada: Botões Inline & Radar a funcionar!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. CREDENCIAIS (Token fixo guardado)
TOKEN = '8898446380:AAGUG8IDi-XV2cUx3M9BqZFw-z9CIcSJVsw'
CANAL_ID = '@setupdaestrada'
LINK_REVOLUT = 'https://revolut.me/guilhevb38'
USERNAME_BOT = 'Setup_da_Estrada_Bot' # Corrigido com sublinhados obrigatórios

bot = telebot.TeleBot(TOKEN)

# 3. GESTÃO DE DADOS (JSON)
def carregar_json(ficheiro):
    try:
        with open(ficheiro, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {} if ficheiro == 'utilizadores.json' else []

def guardar_json(ficheiro, dados):
    with open(ficheiro, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def formatar_promo(promo):
    return f"🔥 **OPORTUNIDADE** 🔥\n📦 **Produto:** {promo['nome']}\n\n❌ **Preço Habitual:** ~{promo['preco_antigo']}~\n✅ **Preço de Desconto:** {promo['preco_novo']}\n\n👉 **[Ver na Amazon com Desconto]({promo['link']})**"

# 4. PAINEL COM BOTÕES DIRETAMENTE NO CHAT (Inline Keyboards)
@bot.message_handler(commands=['start', 'menu'])
def painel_privado(message):
    if message.chat.type != 'private':
        return 
        
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_promo = types.InlineKeyboardButton("🔥 Ver Promoção", callback_data='cmd_promo')
    btn_chuva = types.InlineKeyboardButton("🌧️ Equipamento Chuva", callback_data='cmd_chuva')
    btn_dica = types.InlineKeyboardButton("💡 Dica da Estrada", callback_data='cmd_dica')
    btn_alertas = types.InlineKeyboardButton("⛈️ Configurar Alertas", callback_data='cmd_cidade_info')
    btn_cafe = types.InlineKeyboardButton("☕ Pagar um Café", url=LINK_REVOLUT)
    btn_clear = types.InlineKeyboardButton("🧹 Limpar / Reiniciar", callback_data='cmd_clear')
    
    markup.add(btn_promo, btn_chuva, btn_dica, btn_alertas, btn_cafe, btn_clear)
    
    msg = f"""
⚡ **CENTRO DE COMANDO - SETUP DA ESTRADA** ⚡

Olá, estafeta! Clica nos botões abaixo para interagir diretamente com o sistema:
    """
    bot.send_message(message.chat.id, text=msg, parse_mode='Markdown', reply_markup=markup)

# 5. GESTÃO DOS CLIQUES DOS BOTÕES NO CHAT
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if call.data == 'cmd_promo':
        produtos = carregar_json('produtos.json')
        if produtos:
            prod = random.choice(produtos)
            bot.send_photo(chat_id, photo=prod['imagem'], caption=formatar_promo(prod), parse_mode='Markdown')
            
    elif call.data == 'cmd_chuva':
        produtos = carregar_json('produtos.json')
        produtos_chuva = [p for p in produtos if p.get('categoria') == 'chuva']
        if produtos_chuva:
            prod = random.choice(produtos_chuva)
            bot.send_photo(chat_id, photo=prod['imagem'], caption=formatar_promo(prod), parse_mode='Markdown')
            
    elif call.data == 'cmd_dica':
        dicas = carregar_json('dicas.json')
        if dicas:
            dica = random.choice(dicas)
            bot.send_message(chat_id, text=f"💡 **DICA DA ESTRADA** 💡\n\n{dica}", parse_mode='Markdown')
            
    elif call.data == 'cmd_cidade_info':
        aviso = "📍 **RADAR METEOROLÓGICO**\n\nPara ativar os alertas automáticos de chuva, escreve apenas o nome da tua cidade (ex: *Coimbra* ou *Lousã*)."
        bot.send_message(chat_id, text=aviso, parse_mode='Markdown')
        
    elif call.data == 'cmd_clear':
        chat_id_str = str(chat_id)
        utilizadores = carregar_json('utilizadores.json')
        if chat_id_str in utilizadores:
            del utilizadores[chat_id_str]
            guardar_json('utilizadores.json', utilizadores)
        bot.send_message(chat_id, "🧹 **Memória limpa!** O teu registo de cidade foi apagado.", parse_mode='Markdown')
        
    bot.answer_callback_query(call.id)

# 6. COMANDO /clear POR TEXTO
@bot.message_handler(commands=['clear'])
def comando_clear_texto(message):
    if message.chat.type != 'private':
        return
    chat_id = str(message.chat.id)
    utilizadores = carregar_json('utilizadores.json')
    if chat_id in utilizadores:
        del utilizadores[chat_id]
        guardar_json('utilizadores.json', utilizadores)
    bot.send_message(message.chat.id, "🧹 **Memória limpa!** O teu registo de cidade foi apagado.", parse_mode='Markdown')

# 7. GESTÃO DO TEXTO DA CIDADE (Para o Radar)
@bot.message_handler(func=lambda message: message.chat.type == 'private' and not message.text.startswith('/'))
def capturar_cidade(message):
    cidade = message.text.strip()
    chat_id = str(message.chat.id)
    
    utilizadores = carregar_json('utilizadores.json')
    utilizadores[chat_id] = cidade
    guardar_json('utilizadores.json', utilizadores)
    
    bot.send_message(message.chat.id, f"✅ **Radar Ativo!** Estás registado para receber avisos de temporal em: **{cidade.title()}** 🚀")

# 8. MOTOR DO RADAR (Background)
def radar_meteorologico():
    print("🌤️ Radar Meteorológico ativado!")
    cidades_em_alerta = {} 
    time.sleep(20)
    
    while True:
        try:
            utilizadores = carregar_json('utilizadores.json')
            cidades_unicas = list(set([c.lower() for c in utilizadores.values()]))
            
            for cidade in cidades_unicas:
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt&format=json"
                geo_req = requests.get(geo_url).json()
                
                if 'results' in geo_req:
                    lat = geo_req['results'][0]['latitude']
                    lon = geo_req['results'][0]['longitude']
                    nome_real = geo_req['results'][0]['name']
                    
                    meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=precipitation,wind_speed_10m"
                    meteo_req = requests.get(meteo_url).json()
                    
                    chuva_agora = meteo_req['current']['precipitation'] 
                    vento_agora = meteo_req['current']['wind_speed_10m'] 
                    
                    tempo_mau = chuva_agora >= 0.5 or vento_agora >= 35.0
                    estado_anterior = cidades_em_alerta.get(cidade, False)
                    
                    if tempo_mau and not estado_anterior:
                        alerta = f"⚠️ **ALERTA DE TEMPORAL: {nome_real.upper()}** ⚠️\n\n🌧️ O radar detetou mudança no tempo agora mesmo! Prepara o impermeável e cuidado nas estradas."
                        for u_chat_id, u_cidade in utilizadores.items():
                            if u_cidade.lower() == cidade:
                                try:
                                    bot.send_message(u_chat_id, text=alerta, parse_mode='Markdown')
                                except Exception:
                                    pass 
                        cidades_em_alerta[cidade] = True 
                        
                    elif not tempo_mau and estado_anterior:
                        cidades_em_alerta[cidade] = False 
                        
        except Exception as e:
            print(f"⚠️ Erro no Radar: {e}")
            
        time.sleep(60 * 60)

# 9. MENU AUTOMÁTICO DE INSTRUÇÕES NO CANAL (De 2 em 2 horas)
def auto_menu():
    print("📋 Auto-Menu ativado!")
    time.sleep(15) 
    while True:
        try:
            # Garante que usa a variável USERNAME_BOT corretamente com sublinhados
            msg = f"""
🤖 **COMO USAR ESTE CANAL AO MÁXIMO** 🤖

Sabias que tens um assistente pessoal na estrada? Clica em 👉 @{USERNAME_BOT} ou [neste link](https://t.me/{USERNAME_BOT}) para abrir o teu painel privado. 

Lá encontras botões interativos diretos no chat para:
⛈️ Ativar o Radar de Chuva
🔥 Ver Produtos e Promoções
🌧️ Ver Equipamento de Proteção
💡 Consultar Dicas de Entrega

*Acede já ao chat privado e testa os botões!* 🚀
"""
            bot.send_message(CANAL_ID, text=msg, parse_mode='Markdown', disable_web_page_preview=True)
        except Exception as e:
            print(f"⚠️ Erro no Menu: {e}")
            
        time.sleep(2 * 60 * 60) 

# 10. CICLO DE VENDAS DO CANAL (Background)
def auto_poster():
    print("🤖 Auto-Poster ativado!")
    time.sleep(10)
    while True:
        try:
            hora_atual = datetime.now().hour
            produtos = carregar_json('produtos.json')
            dicas = carregar_json('dicas.json')
            
            if 12 <= hora_atual <= 14 and dicas:
                dica = random.choice(dicas)
                bot.send_message(CANAL_ID, f"💡 **DICA DA HORA DE ALMOÇO** 💡\n\n{dica}", parse_mode='Markdown')
            elif 20 <= hora_atual <= 23:
                premium = [p for p in produtos if p.get('premium') == True]
                if premium:
                    prod = random.choice(premium)
                    bot.send_photo(CANAL_ID, photo=prod['imagem'], caption=formatar_promo(prod), parse_mode='Markdown')
            else:
                if produtos:
                    prod = random.choice(produtos)
                    bot.send_photo(CANAL_ID, photo=prod['imagem'], caption=formatar_promo(prod), parse_mode='Markdown')
        except Exception as e:
            print(f"⚠️ Erro detalhado no Auto-Poster: {e}")
            
        time.sleep(4 * 60)

# 11. INICIAR TODAS AS TAREFAS
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=auto_poster, daemon=True).start()
    threading.Thread(target=radar_meteorologico, daemon=True).start()
    threading.Thread(target=auto_menu, daemon=True).start() 
    
    print("🎧 Bot online com Botões Inline no Chat e Link Corrigido...")
    bot.infinity_polling(skip_pending=True)
