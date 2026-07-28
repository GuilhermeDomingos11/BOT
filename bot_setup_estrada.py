import telebot
import time
import random
import os
import json
from datetime import datetime
from flask import Flask
import threading

# 1. SERVIDOR FLASK
app = Flask('')
@app.route('/')
def home():
    return "🤖 Servidor Flask e Bot a funcionar em simultâneo!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. CREDENCIAIS E LINKS
TOKEN = '8898446380:AAGUG8IDi-XV2cUx3M9BqZFw-z9CIcSJVsw'
CANAL_ID = '@setupdaestrada'
LINK_REVOLUT = 'https://revolut.me/guilhevb38' # Substitui pelo teu link do Revolut

bot = telebot.TeleBot(TOKEN)

# 3. CARREGAR DADOS (ARQUITETURA JSON)
def carregar_json(ficheiro):
    with open(ficheiro, 'r', encoding='utf-8') as f:
        return json.load(f)

# 4. FUNÇÕES DE FORMATAÇÃO
def formatar_promo(promo):
    return f"""
🔥 **OPORTUNIDADE** 🔥
📦 **Produto:** {promo['nome']}

❌ **Preço Habitual:** ~{promo['preco_antigo']}~
✅ **Preço de Desconto:** {promo['preco_novo']}

👉 **[Ver na Amazon com Desconto]({promo['link']})**
"""

# 5. COMANDOS INTERATIVOS DO UTILIZADOR
@bot.message_handler(commands=['promo'])
def comando_promo(message):
    produtos = carregar_json('produtos.json')
    produto = random.choice(produtos)
    bot.send_photo(message.chat.id, photo=produto['imagem'], caption=formatar_promo(produto), parse_mode='Markdown')

@bot.message_handler(commands=['chuva'])
def comando_chuva(message):
    produtos = carregar_json('produtos.json')
    produtos_chuva = [p for p in produtos if p.get('categoria') == 'chuva']
    if produtos_chuva:
        produto = random.choice(produtos_chuva)
        bot.send_photo(message.chat.id, photo=produto['imagem'], caption=formatar_promo(produto), parse_mode='Markdown')

@bot.message_handler(commands=['dica'])
def comando_dica(message):
    dicas = carregar_json('dicas.json')
    dica = random.choice(dicas)
    msg = f"💡 **DICA DA ESTRADA** 💡\n\n{dica}"
    bot.send_message(message.chat.id, text=msg, parse_mode='Markdown')

@bot.message_handler(commands=['cafe'])
def comando_cafe(message):
    msg = f"""
☕ **Gostaste das dicas ou poupaste dinheiro com o bot?** 

Se quiseres dar uma força ao projeto, podes pagar-me um café rapidamente e sem taxas através do Revolut:
👉 **[Pagar um Café pelo Revolut]({LINK_REVOLUT})**

Obrigado pela força e boas entregas! 🚀
"""
    bot.send_message(message.chat.id, text=msg, parse_mode='Markdown', disable_web_page_preview=True)

# 6. CICLO INTELIGENTE AUTOMÁTICO (THREAD SEPARADA)
def auto_poster():
    print("🤖 Modo Automático Iniciado.")
    time.sleep(10)
    
    while True:
        try:
            hora_atual = datetime.now().hour
            produtos = carregar_json('produtos.json')
            dicas = carregar_json('dicas.json')
            
            # Lógica de Horários
            if 12 <= hora_atual <= 14:
                # Hora de almoço: Postar uma dica
                dica = random.choice(dicas)
                bot.send_message(CANAL_ID, f"💡 **DICA DA HORA DE ALMOÇO** 💡\n\n{dica}", parse_mode='Markdown')
            
            elif 20 <= hora_atual <= 23:
                # Noite: Postar produtos Premium (maior comissão quando o pessoal está em casa)
                premium = [p for p in produtos if p.get('premium') == True]
                if premium:
                    prod = random.choice(premium)
                    bot.send_photo(CANAL_ID, photo=prod['imagem'], caption=formatar_promo(prod), parse_mode='Markdown')
            
            else:
                # Resto do dia: Publicação normal
                prod = random.choice(produtos)
                bot.send_photo(CANAL_ID, photo=prod['imagem'], caption=formatar_promo(prod), parse_mode='Markdown')
                
        except Exception as e:
            print(f"⚠️ Erro no Auto-Poster: {e}")
            
        time.sleep(30 * 60) # Pausa de 30 minutos

# 7. INICIAR TODAS AS TAREFAS
if __name__ == "__main__":
    # Arranca o servidor Flask
    t_flask = threading.Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()
    
    # Arranca as publicações automáticas
    t_poster = threading.Thread(target=auto_poster)
    t_poster.daemon = True
    t_poster.start()
    
    # Mantém o Bot à escuta dos comandos dos utilizadores
    print("🎧 Bot à escuta de comandos...")
    bot.polling(non_stop=True)
