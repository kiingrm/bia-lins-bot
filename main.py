import telebot
from openai import OpenAI
import time
import threading
import random
import traceback
import os
import logging

# ============================================
# LOGS
# ============================================

logging.basicConfig(level=logging.INFO)

# ============================================
# VARIÁVEIS DE AMBIENTE
# ============================================

OPENAI_KEY = os.getenv("OPENAI_KEY")
TELEGRAM_BOT_KEY = os.getenv("TELEGRAM_BOT_KEY")
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID"))
VIP_LINK = os.getenv("VIP_LINK")

if not OPENAI_KEY:
    raise Exception("OPENAI_KEY não encontrada")

if not TELEGRAM_BOT_KEY:
    raise Exception("TELEGRAM_BOT_KEY não encontrada")

# ============================================
# ÁUDIOS
# ============================================

AUDIO_START = "start.ogg"
AUDIO_HOT = "hot.ogg"

# ============================================
# BOT / OPENAI
# ============================================

bot = telebot.TeleBot(TELEGRAM_BOT_KEY)
openai_client = OpenAI(api_key=OPENAI_KEY)

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
# PROMPT
# ============================================

PROMPT_BIA = """
Você é Bia Lins, 26 anos, de Salvador.

Você conversa como uma mulher real no Telegram:
casual, natural e provocante.

Nunca diga que é IA.
Nunca seja robótica.
Nunca interrogue demais.

Seu objetivo é criar conexão e conduzir naturalmente pro VIP.
"""

# ============================================
# DETECTAR INTERESSE VIP
# ============================================

def tem_interesse_vip(texto: str) -> bool:

    texto_lower = texto.lower()

    palavras = [
        "vip",
        "víp",
        "link",
        "acesso",
        "quero ver",
        "manda o link",
        "conteúdo",
        "pelada",
        "quero o vip"
    ]

    return any(p in texto_lower for p in palavras)

# ============================================
# ENVIAR ÁUDIO START
# ============================================

def enviar_audio_start(chat_id):

    try:

        if os.path.exists(AUDIO_START):

            with open(AUDIO_START, 'rb') as audio:
                bot.send_voice(chat_id, audio)

    except Exception as e:

        print(f"ERRO AUDIO START: {e}")
        traceback.print_exc()

# ============================================
# ENVIAR VIP
# ============================================

def enviar_vip(chat_id):

    if vip_enviado.get(chat_id, False):
        return False

    try:

        if os.path.exists(AUDIO_HOT):

            with open(AUDIO_HOT, 'rb') as audio:
                bot.send_voice(chat_id, audio)

            time.sleep(2)

        texto = (
            "ai amor... 😩\n\n"
            "no VIP eu posto tudo sem censura...\n"
            "vídeos gozando, masturbando e muito mais 😈"
        )

        bot.send_message(chat_id, texto)

        time.sleep(1)

        bot.send_message(chat_id, VIP_LINK)

        vip_enviado[chat_id] = True

        return True

    except Exception as e:

        print(f"ERRO VIP: {e}")
        traceback.print_exc()

        return False

# ============================================
# ATUALIZAR LOG
# ============================================

def atualizar_log(chat_id, user_name):

    try:

        hist_texto = "\n".join(
            historico_conversas.get(chat_id, [])
        )

        if len(hist_texto) > 3000:
            hist_texto = hist_texto[-3000:]

        texto_log = f"👤 {user_name}\n\n{hist_texto}"

        markup = telebot.types.InlineKeyboardMarkup()

        markup.add(
            telebot.types.InlineKeyboardButton(
                "📜 Histórico",
                callback_data=f"hist_{chat_id}"
            )
        )

        if chat_id in log_message_ids:

            try:

                bot.edit_message_text(
                    text=texto_log,
                    chat_id=LOG_CHAT_ID,
                    message_id=log_message_ids[chat_id],
                    reply_markup=markup
                )

            except:
                pass

        else:

            msg = bot.send_message(
                LOG_CHAT_ID,
                texto_log,
                reply_markup=markup
            )

            log_message_ids[chat_id] = msg.message_id

    except Exception as e:

        print(f"ERRO LOG: {e}")

# ============================================
# PROCESSAR RESPOSTA
# ============================================

def processar_resposta_final(chat_id):

    try:

        if chat_id not in mensagens_pendentes:
            return

        if not mensagens_pendentes[chat_id]:
            return

        mensagens = mensagens_pendentes[chat_id]

        mensagens_pendentes[chat_id] = []

        texto_usuario = " ".join(mensagens).strip()

        if len(texto_usuario) < 2:
            return

        contador_mensagens[chat_id] = (
            contador_mensagens.get(chat_id, 0) + 1
        )

        memoria_contexto[chat_id].append({
            "role": "user",
            "content": texto_usuario
        })

        historico_conversas[chat_id].append(
            f"👤 Lead: {texto_usuario}"
        )

        # ====================================
        # INTERESSE VIP
        # ====================================

        if tem_interesse_vip(texto_usuario):

            enviar_vip(chat_id)

            memoria_contexto[chat_id].append({
                "role": "assistant",
                "content": "[VIP ENVIADO]"
            })

            historico_conversas[chat_id].append(
                "🤖 Bia: [VIP ENVIADO]"
            )

            atualizar_log(chat_id, "Lead")

            return

        # ====================================
        # DIGITANDO
        # ====================================

        bot.send_chat_action(chat_id, "typing")

        time.sleep(random.randint(2, 4))

        # ====================================
        # 20ª MSG -> VIP
        # ====================================

        if contador_mensagens[chat_id] >= 20:

            enviar_vip(chat_id)

            return

        # ====================================
        # OPENAI
        # ====================================

        resposta = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                memoria_contexto[chat_id][0]
            ] + memoria_contexto[chat_id][-10:],
            max_tokens=140,
            temperature=0.78
        )

        texto_resposta = resposta.choices[0].message.content

        bot.send_message(chat_id, texto_resposta)

        memoria_contexto[chat_id].append({
            "role": "assistant",
            "content": texto_resposta
        })

        historico_conversas[chat_id].append(
            f"🤖 Bia: {texto_resposta}"
        )

        atualizar_log(chat_id, "Lead")

    except Exception as e:

        print(f"ERRO IA ({chat_id}): {e}")
        traceback.print_exc()

# ============================================
# START
# ============================================

@bot.message_handler(commands=['start'])
def comando_start(message):

    try:

        chat_id = message.chat.id

        memoria_contexto[chat_id] = [
            {
                "role": "system",
                "content": PROMPT_BIA
            }
        ]

        historico_conversas[chat_id] = []
        mensagens_pendentes[chat_id] = []
        contador_mensagens[chat_id] = 0
        vip_enviado[chat_id] = False

        delay = random.randint(30, 90)

        threading.Timer(
            delay,
            enviar_audio_start,
            args=[chat_id]
        ).start()

        atualizar_log(
            chat_id,
            message.from_user.first_name
        )

        print(f"NOVO CHAT: {chat_id}")

    except Exception as e:

        print(f"ERRO START: {e}")
        traceback.print_exc()

# ============================================
# CONVERSA
# ============================================

@bot.message_handler(func=lambda message: True)
def conversar(message):

    try:

        chat_id = message.chat.id

        if chat_id not in memoria_contexto:
            return

        if not message.text:
            return

        texto = message.text.strip()

        if len(texto) < 2:
            return

        if chat_id not in mensagens_pendentes:
            mensagens_pendentes[chat_id] = []

        mensagens_pendentes[chat_id].append(texto)

        if chat_id in timers:
            timers[chat_id].cancel()

        timers[chat_id] = threading.Timer(
            12,
            processar_resposta_final,
            args=[chat_id]
        )

        timers[chat_id].start()

    except Exception as e:

        print(f"ERRO MSG: {e}")
        traceback.print_exc()

# ============================================
# HISTÓRICO
# ============================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("hist_")
)
def mostrar_historico(call):

    try:

        chat_id = int(
            call.data.split("_")[1]
        )

        historico = "\n".join(
            historico_conversas.get(chat_id, [])
        )

        if len(historico) > 4000:
            historico = historico[-4000:]

        bot.send_message(
            call.message.chat.id,
            f"📜 HISTÓRICO\n\n{historico}"
        )

    except Exception as e:

        print(f"ERRO HIST: {e}")
        traceback.print_exc()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":

    print("BOT ONLINE")

    while True:

        try:

            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                skip_pending=True,
                allowed_updates=[
                    "message",
                    "callback_query"
                ]
            )

        except Exception as e:

            print(f"ERRO POLLING: {e}")

            traceback.print_exc()

            time.sleep(10)
