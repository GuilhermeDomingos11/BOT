import telebot
import time
import random
import os
from flask import Flask
import threading

# Servidor Flask simples para manter a aplicação sempre acordada na nuvem
app = Flask('')

@app.route('/')
def home():
    return "🤖 Bot Setup da Estrada a funcionar a 100% na nuvem!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# -------------------------------------------------------------
# 1. CREDENCIAIS E CONFIGURAÇÕES
# -------------------------------------------------------------
TOKEN = '8898446380:AAGUG8IDi-XV2cUx3M9BqZFw-z9CIcSJVSw'
CANAL_ID = '@setupdaestrada'
TAG_AFILIADO = 'setupdaestrada-21'

bot = telebot.TeleBot(TOKEN)

# -------------------------------------------------------------
# 2. CATÁLOGO DE PRODUTOS
# -------------------------------------------------------------
lista_promocoes = [
    {
        "nome": "Powerbank 20000mAh de Alta Capacidade para Turnos Longos",
        "preco_antigo": "49.99€",
        "preco_novo": "34.99€",
        "link": f"https://www.amazon.es/s?k=powerbank+20000mah+carga+rapida&tag={TAG_AFILIADO}",
        "imagem": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?q=80&w=800&auto=format&fit=crop"
    },
    {
        "nome": "Suporte de Telemóvel para Mota com Amortecedor de Vibração",
        "preco_antigo": "59.90€",
        "preco_novo": "45.00€",
        "link": f"https://www.amazon.es/s?k=suporte+telemovel+mota+antivibracao&tag={TAG_AFILIADO}",
        "imagem": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?q=80&w=800&auto=format&fit=crop"
    },
    {
        "nome": "Cadeado de Disco para Mota com Alarme Sonoro Sensível",
        "preco_antigo": "39.99€",
        "preco_novo": "24.99€",
        "link": f"https://www.amazon.es/s?k=cadeado+disco+mota+alarme&tag={TAG_AFILIADO}",
        "imagem": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?q=80&w=800&auto=format&fit=crop"
    },
    {
        "nome": "Luvas Térmicas e Impermeáveis para Inverno e Chuva",
        "preco_antigo": "45.00€",
        "preco_novo": "29.99€",
        "link": f"https://www.amazon.es/s?k=luvas+impermeaveis+mota+inverno&tag={TAG_AFILIADO}",
        "imagem": "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?q=80&w=800&auto=format&fit=crop"
    },
    {
        "nome": "Intercomunicador Bluetooth para Capacete de Mota",
        "preco_antigo": "89.99€",
        "preco_novo": "59.99€",
        "link": f"https://www.amazon.es/s?k=intercomunicador+capacete+mota&tag={TAG_AFILIADO}",
        "imagem": "https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=800&auto=format&fit=crop"
    },
    {
        "nome": "Carregador USB Duplo de Instalação no Guiador da Mota",
        "preco_antigo": "25.00€",
        "preco_novo": "15.99€",
        "link": f"https://www.amazon.es/s?k=carregador+usb+guiador+mota&tag={TAG_AFILIADO}",
        "imagem": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?q=80&w=800&auto=format&fit=crop"
    },
    {
        "nome": "Capa de Chuva Completa Impermeável para Motociclistas",
        "preco_antigo": "40.00€",
        "preco_novo": "26.99€",
        "link": f"https://www.amazon.es/s?k=capa+chuva+completa+mota&tag={TAG_AFILIADO}",
        "imagem": "https://images.unsplash.com/photo-1558981285-6f0c94958bb6?q=80&w=800&auto=format&fit=crop"
    }
]

# -------------------------------------------------------------
# 3. FUNÇÃO DE PUBLICAÇÃO
# -------------------------------------------------------------
def publicar_promocao(promo):
    mensagem = f"""
🔥 **SETUP DA ESTRADA: OPORTUNIDADE** 🔥

📦 **Produto:** {promo['nome']}

❌ **Preço Habitual:** ~{promo['preco_antigo']}~
✅ **Preço de Desconto:** {promo['preco_novo']}

👉 **[Ver Opções na Amazon com Desconto]({promo['link']})**
    """
    try:
        bot.send_photo(
            chat_id=CANAL_ID, 
            photo=promo['imagem'], 
            caption=mensagem, 
            parse_mode='Markdown'
        )
        print(f"✅ Publicado com sucesso: {promo['nome']}")
    except Exception as erro:
        print(f"❌ Erro ao publicar: {erro}")

# -------------------------------------------------------------
# 4. CICLO DO BOT EM BACKGROUND
# -------------------------------------------------------------
def loop_bot():
    print("🤖 Bot 'Setup da Estrada' iniciado em background...")
    historico_recentes = []
    
    # Pausa inicial para garantir que o servidor web subiu primeiro
    time.sleep(10)
    
    while True:
        try:
            produtos_disponiveis = [p for p in lista_promocoes if p['nome'] not in historico_recentes]
            if not produtos_disponiveis:
                produtos_disponiveis = lista_promocoes
                historico_recentes.clear()
                
            produto_escolhido = random.choice(produtos_disponiveis)
            publicar_promocao(produto_escolhido)
            
            historico_recentes.append(produto_escolhido['nome'])
            if len(historico_recentes) > 3:
                historico_recentes.pop(0)
        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")
            
        # Intervalo de 30 minutos entre publicações
        time.sleep(15 * 60)

if __name__ == "__main__":
    # Arranca o bot do Telegram numa thread separada
    t = threading.Thread(target=loop_bot)
    t.daemon = True
    t.start()
    
    # Arranca o servidor Flask na thread principal (obrigatório para o Render)
    run_flask()
