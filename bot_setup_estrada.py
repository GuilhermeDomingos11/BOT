import telebot
import time
import random
import os
from flask import Flask
import threading

# -------------------------------------------------------------
# 1. SERVIDOR FLASK (Para a nuvem não adormecer)
# -------------------------------------------------------------
app = Flask('')

@app.route('/')
def home():
    return "🤖 Bot Setup da Estrada a funcionar a 100% na nuvem!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# -------------------------------------------------------------
# 2. CREDENCIAIS E CONFIGURAÇÕES
# -------------------------------------------------------------
TOKEN = '8898446380:AAGUG8IDi-XV2cUx3M9BqZFw-z9CIcSJVsw'
CANAL_ID = '@setupdaestrada'
TAG_AFILIADO = 'setupdaestrad-21'

bot = telebot.TeleBot(TOKEN)

# -------------------------------------------------------------
# 3. CATÁLOGOS (PRODUTOS E DICAS)
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

lista_dicas = [
    "📦 **Organização da Top Box:** Top boxes rígidas são excelentes para a segurança, mas os pedidos pequenos balançam muito. Leva sempre uma toalha limpa grossa ou plástico de bolhas para preencheres o espaço vazio. Evita molhos derramados em ruas de calçada!",
    "⛈️ **Tração na Chuva:** A calçada portuguesa molhada e as grelhas de esgoto são os maiores inimigos nas subidas íngremes. Nestes dias, reduz a pressão dos pneus ligeiramente (cerca de 2 a 3 psi) para ganhares mais superfície de contacto e aderência.",
    "🔋 **Frio e Baterias:** Nos turnos de inverno, o frio drena a bateria do telemóvel até 30% mais rápido. Mantém a tua powerbank perto do corpo (dentro do casaco) e passa apenas o cabo para fora, o calor corporal ajuda a manter a eficiência da bateria.",
    "🏍️ **Corrente Saudável:** Apanhaste uma bátega de água a meio do turno? Assim que chegares a casa, passa um spray lubrificante na corrente enquanto ela ainda está quente. Evita ferrugem e poupa-te muitos euros na oficina a longo prazo.",
    "🚦 **Olhos na Estrada:** Em cruzamentos cegos ou entroncamentos apertados, não olhes só para os carros, olha para os reflexos nas montras das lojas. Muitas vezes consegues ver se vem lá um carro antes sequer de ele chegar à esquina.",
    "🍔 **Gestão de Restaurantes:** O restaurante disse 'são só mais 5 minutinhos'? Aproveita esse tempo para verificares a pressão dos pneus, limpar a viseira do capacete ou responderes a mensagens. O tempo de espera é o teu tempo de manutenção."
]

# -------------------------------------------------------------
# 4. FUNÇÕES DE PUBLICAÇÃO
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
        bot.send_photo(chat_id=CANAL_ID, photo=promo['imagem'], caption=mensagem, parse_mode='Markdown')
        print(f"✅ Produto publicado: {promo['nome']}")
    except Exception as erro:
        print(f"❌ Erro ao publicar produto: {erro}")

def publicar_dica(dica):
    mensagem = f"""
💡 **DICA DA ESTRADA** 💡

{dica}

👉 *Partilha o canal com os teus colegas para não perderem as dicas e os descontos!*
    """
    try:
        bot.send_message(chat_id=CANAL_ID, text=mensagem, parse_mode='Markdown')
        print("✅ Dica publicada com sucesso!")
    except Exception as erro:
        print(f"❌ Erro ao publicar dica: {erro}")

# -------------------------------------------------------------
# 5. CICLO DO BOT EM BACKGROUND (COM INTELIGÊNCIA)
# -------------------------------------------------------------
def loop_bot():
    print("🤖 Bot 'Setup da Estrada' iniciado! Misto de Ofertas e Dicas a rodar.")
    historico_recentes = []
    historico_dicas = []
    
    contador_ciclos = 1
    
    # Pausa inicial
    time.sleep(10)
    
    while True:
        try:
            # A cada 5 ciclos (ex: 5 produtos publicados), publica uma dica em vez de um produto
            if contador_ciclos % 5 == 0:
                dicas_disponiveis = [d for d in lista_dicas if d not in historico_dicas]
                if not dicas_disponiveis:
                    dicas_disponiveis = lista_dicas
                    historico_dicas.clear()
                    
                dica_escolhida = random.choice(dicas_disponiveis)
                publicar_dica(dica_escolhida)
                historico_dicas.append(dica_escolhida)
            
            # Caso contrário, publica a promoção normal
            else:
                produtos_disponiveis = [p for p in lista_promocoes if p['nome'] not in historico_recentes]
                if not produtos_disponiveis:
                    produtos_disponiveis = lista_promocoes
                    historico_recentes.clear()
                    
                produto_escolhido = random.choice(produtos_disponiveis)
                publicar_promocao(produto_escolhido)
                historico_recentes.append(produto_escolhido['nome'])
                
                if len(historico_recentes) > 3:
                    historico_recentes.pop(0)
            
            contador_ciclos += 1
            
        except Exception as e:
            print(f"⚠️ Erro no ciclo: {e}")
            
        # Podes alterar este valor. 30 * 60 = 30 minutos.
        time.sleep(2 * 60)

if __name__ == "__main__":
    t = threading.Thread(target=loop_bot)
    t.daemon = True
    t.start()
    
    run_flask()
