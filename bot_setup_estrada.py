import telebot
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
    return "🤖 Setup da Estrada: Modo Vendas, Radar e Menu a funcionar!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. CREDENCIAIS
TOKEN = '8898446380:AAGUG8IDi-XV2cUx3M9BqZFw-z9CIcSJVSw'
CANAL_ID = '@setupdaestrada'
LINK_REVOLUT = 'https://revolut.me/guilhevb38'
USERNAME_BOT = 'Setup_da_Estrada_Bot' 

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

# 4. COMANDOS DE LOJA E COMUNIDADE (Para o Canal e Privado)
@bot.message_handler(commands=['promo', 'chuva', 'dica', 'cafe'])
def comandos_basicos(message):
    comando = message.text.split()[0].lower()
    
    if comando == '/promo':
        produtos = carregar_json('produtos.json')
        if produtos:
            prod = random.choice(produtos)
            bot.send_photo(message.chat.id, photo=prod['imagem'], caption=formatar_promo(prod), parse_mode='Markdown')
            
    elif comando == '/chuva':
        produtos = carregar_json('produtos.json')
        produtos_chuva = [p for p in produtos if p.get('categoria') == 'chuva']
        if produtos_chuva:
            prod = random.choice(produtos_chuva)
            bot.send_photo(message.chat.id, photo=prod['imagem'], caption=formatar_promo(prod), parse_mode='Markdown')
            
    elif comando == '/dica':
        dicas = carregar_json('dicas.json')
        if dicas:
            dica = random.choice(dicas)
            bot.send_message(message.chat.id, text=f"💡 **DICA DA ESTRADA** 💡\n\n{dica}", parse_mode='Markdown')
            
    elif comando == '/cafe':
        msg = f"☕ **Gostaste das dicas ou poupaste dinheiro?**\nPodes dar uma força ao projeto pagando-me um café sem taxas pelo Revolut:\n👉 **[Pagar um Café pelo Revolut]({LINK_REVOLUT})**\n\nObrigado e boas entregas! 🚀"
        bot.send_message(message.chat.id, text=msg, parse_mode='Markdown', disable_web_page_preview=True)

# 5. NOVO SISTEMA: ALERTAS METEOROLÓGICOS (Apenas em Privado)
@bot.message_handler(commands=['alertas'])
def comando_alertas(message):
    msg = """
⛈️ **BEM-VINDO AO RADAR DO ESTAFETA** ⛈️

Nunca mais sejas apanhado de surpresa! O bot vai enviar-te uma mensagem privada sempre que estiver a chegar chuva ou vento forte à tua zona.

Para te registares, escreve **/cidade** seguido do nome da tua cidade.
*Exemplo:* `/cidade Coimbra` ou `/cidade Lousã`
    """
    bot.send_message(message.chat.id, text=msg, parse_mode='Markdown')

@bot.message_handler(commands=['cidade'])
def comando_cidade(message):
    try:
        cidade = message.text.split(' ', 1)[1].strip()
        chat_id = str(message.chat.id)
        
        utilizadores = carregar_json('utilizadores.json')
        utilizadores[chat_id] = cidade
        guardar_json('utilizadores.json', utilizadores)
        
        bot.send_message(message.chat.id, f"✅ **Perfeito!** Estás registado para receber alertas meteorológicos para: **{cidade.title()}**.\nMal o tempo feche, eu aviso-te aqui!")
    except IndexError:
        bot.send_message(message.chat.id, "⚠️ Erro! Tens de escrever a cidade. Exemplo: `/cidade Coimbra`", parse_mode='Markdown')

# 6. MOTOR DO RADAR (Corre em background)
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
                        alerta = f"⚠️ **ALERTA DE TEMPORAL: {nome_real.upper()}** ⚠️\n\n🌧️ O radar detetou mudança no tempo agora mesmo! Prepara o impermeável e tem cuidado nas grelhas metálicas e calçadas."
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

# 7. MENU AUTOMÁTICO DE INSTRUÇÕES (Corre em background - De 2 em 2 horas)
def auto_menu():
    print("📋 Auto-Menu ativado!")
    time.sleep(15) 
    while True:
        try:
            msg = f"""
🤖 **COMO USAR ESTE CANAL AO MÁXIMO** 🤖

Sabias que podes pedir coisas ao bot a qualquer momento? Clica aqui 👉 @{USERNAME_BOT} ou [neste link](https://t.me/{USERNAME_BOT}) e manda-lhe uma mensagem privada com estes comandos:

🌦️ **/alertas** - Liga o radar de chuva para a tua cidade!
🌧️ **/chuva** - Pede equipamento apenas para a chuva.
🔥 **/promo** - Pede um desconto surpresa.
💡 **/dica** - Pede um truque para as entregas.
☕ **/cafe** - Ajuda o projeto com um café.

*Testa agora mesmo! Vai ao chat do bot e escreve /alertas* 🚀
"""
            bot.send_message(CANAL_ID, text=msg, parse_mode='Markdown', disable_web_page_preview=True)
        except Exception as e:
            print(f"⚠️ Erro no Menu: {e}")
            
        time.sleep(2 * 60 * 60) 

# 8. CICLO DE VENDAS DO CANAL (Corre em background)
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
            
        time.sleep(30 * 60)

# 9. INICIAR TODAS AS TAREFAS
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=auto_poster, daemon=True).start()
    threading.Thread(target=radar_meteorologico, daemon=True).start()
    threading.Thread(target=auto_menu, daemon=True).start() 
    
    print("🎧 Bot online e à escuta...")
    bot.infinity_polling(skip_pending=True)
