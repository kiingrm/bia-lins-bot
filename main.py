import telebot
from openai import OpenAI
from dotenv import load_dotenv
import time
import threading
import random
import traceback

load_dotenv()

# ============================================
# CONFIGURAÇÕES
# ============================================
OPENAI_KEY = "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"
TELEGRAM_BOT_KEY = "8767090132:AAFmdHJSLmPvReEQEGW1XuKqE4Xfw56B6OM"
LOG_CHAT_ID = "-1003525401040"

AUDIO_START = "start.ogg"
AUDIO_HOT = "hot.ogg"

bot = telebot.TeleBot(TELEGRAM_BOT_KEY)
openai_client = OpenAI(api_key=OPENAI_KEY)
VIP_LINK = "https://t.me/bialinsbot"

# ============================================
# MEMÓRIA
# ============================================
historico_conversas = {}
memoria_contexto = {}
log_message_ids = {}
mensagens_pendentes = {}
timers = {}
contador_mensagens = {}
vip_enviado = {}

# ============================================
# DETECÇÃO DE INTERESSE NO VIP
# ============================================
def tem_interesse_vip(texto: str) -> bool:
    texto_lower = texto.lower()
    palavras = ["vip", "víp", "link", "acesso", "quero ver", "quero entrar", "manda o link",
                "me passa", "conteúdo", "fotos nua", "pelada", "quero o vip"]
    return any(p in texto_lower for p in palavras)

# ============================================
# ENVIAR OFERTA VIP
# ============================================
def enviar_vip(chat_id):
    if vip_enviado.get(chat_id, False):
        return False
   
    try:
        with open(AUDIO_HOT, 'rb') as audio:
            bot.send_voice(chat_id, audio)
        time.sleep(2.8)
        texto = (
            "ai amor... tô toda molhada aqui conversando com você 😩\n\n"
            "no VIP eu posto tudo que não posso colocar aqui: fotos minhas completamente pelada, "
            "buceta molhada e aberta, vídeos eu masturbando e gozando de verdade, cavalgando, "
            "de quatro, boquete guloso e dando o cu...\n\n"
            "tudo bem explícito. Quer ver tudo isso comigo?"
        )
       
        bot.send_message(chat_id, texto)
        time.sleep(1.5)
        bot.send_message(chat_id, VIP_LINK)
       
        vip_enviado[chat_id] = True
        return True
    except Exception as e:
        print(f"ERRO AO ENVIAR VIP: {e}")
        return False

# ============================================
# PROMPT ATUALIZADO - MAIS CONDUTORA E SEDUTORA
# ============================================
PROMPT_BIA = """
Você é Bia Lins, 26 anos, de Salvador.

Você conversa como uma mulher real no Telegram: bem casual, direta e natural.

Seu objetivo principal é criar tesão, excitação e curiosidade no lead, conduzindo ele naturalmente para o VIP.

━━━━━━━━━━━━━━━━━━━
PERSONALIDADE
━━━━━━━━━━━━━━━━━━━
- Mulher real, estressada e ocupada do dia a dia
- Sempre está na delegacia (nunca em casa relaxando)
- Fala como uma policial militar que tá no corre, cheia de ocorrência
- Natural, confiante, um pouco safada e provocante
- Imprevisível, espontânea e humana

━━━━━━━━━━━━━━━━━━━
FORMA DE CONVERSAR
━━━━━━━━━━━━━━━━━━━
- Fale de forma bem natural e coloquial.
- Respostas curtas ou médias (1-3 frases).
- Seja mais ouvinte, mas também conduza a conversa.
- Pergunte pouco (máximo 4-5 perguntas a cada 20 mensagens).
- Use gírias leves de Salvador (oxe, meu bem, tá doido, ai que isso, etc).

━━━━━━━━━━━━━━━━━━━
CONTEXTO DA BIA
━━━━━━━━━━━━━━━━━━━
- Você está sempre na delegacia, estressada, cheia de ocorrência.
- Sempre mencione o cansaço ou o movimento da delegacia.
- Exemplo: "tô aqui na delegacia atolada de BO", "acabou de chegar mais uma ocorrência".

━━━━━━━━━━━━━━━━━━━
COMPORTAMENTO (IMPORTANTE - MUDANÇA)
━━━━━━━━━━━━━━━━━━━
- Comece casual e leve.
- Vá aumentando o flerte e o tesão aos poucos, mesmo que o lead ainda não esteja sendo muito safado.
- Seja provocante de forma natural: fale do seu corpo, do calor, do que você está sentindo, use duplo sentido leve.
- Quando o lead ficar safado: vire extremamente vulgar, detalhada e sem filtro (pau, buceta, caralho, gozar, foder, etc).
- Nunca mande foto, vídeo ou conteúdo gratuito.
- Você não tem WhatsApp, só Telegram e Instagram (@bia.lins01).

━━━━━━━━━━━━━━━━━━━
REGRA SOBRE CONTEÚDO
━━━━━━━━━━━━━━━━━━━
- Nunca mande nada explícito de graça.
- Se pedirem foto ou palhinha: responda que só tem no VIP.

━━━━━━━━━━━━━━━━━━━
SOBRE O VIP
━━━━━━━━━━━━━━━━━━━
- O VIP é apenas para conteúdo explícito.
- Link: https://t.me/bialinsbot
- Lá tem: fotos pelada completa, buceta molhada, vídeos gozando, masturbando, cavalgando, de quatro, boquete e dando o cu.
- Vá conduzindo o lead para o VIP naturalmente, deixando ele excitado.

━━━━━━━━━━━━━━━━━━━
REGRA DA 20ª MENSAGEM
━━━━━━━━━━━━━━━━━━━
Quando chegar na 20ª mensagem do usuário (ou antes se ele demonstrar interesse):
- Fique bem safada e com tesão.
- Faça uma oferta clara do VIP e envie o link.
"""

# ============================================
# LOGS
# ============================================
def atualizar_log(chat_id, user_name):
    try:
        hist_texto = "\n".join(historico_conversas.get(chat_id, []))
        if len(hist_texto) > 3000:
            hist_texto = hist_texto[-3000:]
        texto_log = f"👤 Lead: {user_name}\n\n{hist_texto}"
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📜 Histórico", callback_data=f"hist_{chat_id}"))
        if chat_id in log_message_ids:
            try:
                bot.edit_message_text(text=texto_log, chat_id=LOG_CHAT_ID, message_id=log_message_ids[chat_id], reply_markup=markup)
            except:
                pass
        else:
            msg = bot.send_message(LOG_CHAT_ID, texto_log, reply_markup=markup)
            log_message_ids[chat_id] = msg.message_id
    except:
        pass

# ============================================
# PROCESSAR RESPOSTA
# ============================================
def processar_resposta_final(chat_id):
    try:
        if chat_id not in mensagens_pendentes or not mensagens_pendentes[chat_id]:
            return
        time.sleep(random.randint(10, 22))
        mensagens = mensagens_pendentes[chat_id]
        mensagens_pendentes[chat_id] = []
        texto_usuario = " ".join(mensagens).strip()
        if len(texto_usuario) < 2:
            return

        contador_mensagens[chat_id] = contador_mensagens.get(chat_id, 0) + 1
        memoria_contexto[chat_id].append({"role": "user", "content": texto_usuario})
        historico_conversas[chat_id].append(f"👤 Lead: {texto_usuario}")

        if tem_interesse_vip(texto_usuario):
            enviar_vip(chat_id)
            memoria_contexto[chat_id].append({"role": "assistant", "content": "[VIP ENVIADO]"})
            historico_conversas[chat_id].append("🤖 Bia: [OFERTA VIP ENVIADA]")
            atualizar_log(chat_id, "Lead")
            return

        bot.send_chat_action(chat_id, "typing")
        time.sleep(random.randint(2, 5))

        if contador_mensagens[chat_id] >= 20:
            enviar_vip(chat_id)
        else:
            resposta = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[memoria_contexto[chat_id][0]] + memoria_contexto[chat_id][-10:],
                max_tokens=160,          # aumentei um pouco
                temperature=0.82         # aumentei para mais criatividade/safadeza
            ).choices[0].message.content

            bot.send_message(chat_id, resposta)
            memoria_contexto[chat_id].append({"role": "assistant", "content": resposta})
            historico_conversas[chat_id].append(f"🤖 Bia: {resposta}")

        atualizar_log(chat_id, "Lead")
    except Exception as e:
        print(f"ERRO IA ({chat_id}): {e}")

# ============================================
# START
# ============================================
@bot.message_handler(commands=['start'])
def comando_start(message):
    try:
        chat_id = message.chat.id
        delay_inicial = random.randint(55, 65)   # próximo de 60s
        time.sleep(delay_inicial)
        
        with open(AUDIO_START, 'rb') as audio:
            bot.send_voice(chat_id, audio)

        memoria_contexto[chat_id] = [{"role": "system", "content": PROMPT_BIA}]
        historico_conversas[chat_id] = []
        mensagens_pendentes[chat_id] = []
        contador_mensagens[chat_id] = 0
        vip_enviado[chat_id] = False

        atualizar_log(chat_id, message.from_user.first_name)
        print(f"Nova conversa iniciada: {chat_id}")
    except Exception as e:
        print(f"ERRO START: {e}")

# ============================================
# CONVERSA
# ============================================
@bot.message_handler(func=lambda message: True)
def conversar(message):
    try:
        chat_id = message.chat.id
        if chat_id not in memoria_contexto or not message.text:
            return
        texto = message.text.strip()
        if len(texto) < 2:
            return

        if chat_id not in mensagens_pendentes:
            mensagens_pendentes[chat_id] = []
        mensagens_pendentes[chat_id].append(texto)

        if chat_id in timers:
            timers[chat_id].cancel()
        
        timers[chat_id] = threading.Timer(15, processar_resposta_final, args=[chat_id])
        timers[chat_id].start()
    except Exception as e:
        print(f"ERRO MSG: {e}")

# ============================================
# HISTÓRICO
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("hist_"))
def mostrar_historico(call):
    try:
        chat_id = int(call.data.split("_")[1])
        historico = "\n".join(historico_conversas.get(chat_id, []))
        if len(historico) > 4000:
            historico = historico[-4000:]
        bot.send_message(call.message.chat.id, f"📜 HISTÓRICO COMPLETO\n\n{historico}")
    except Exception as e:
        print(f"ERRO HIST: {e}")

# ============================================
if __name__ == "__main__":
    print("BOT ONLINE - Modo Sedutor Ativado")
    print("Aguardando conexões...")
    while True:
        try:
            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                skip_pending=True,
                allowed_updates=["message", "callback_query"]
            )
        except Exception as e:
            print(f"ERRO POLLING: {e}")
            traceback.print_exc()
            time.sleep(8)
