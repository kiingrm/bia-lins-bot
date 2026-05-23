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
                "me passa", "foto", "nude", "pelada", "prévia", "palhinha", "vídeo", "conteúdo"]
    return any(p in texto_lower for p in palavras)

# ============================================
# ENVIAR VIP (bem putona)
# ============================================
def enviar_vip(chat_id):
    if vip_enviado.get(chat_id, False):
        return False

    try:
        texto = (
            "No VIP eu posto tudo bem safado pra você...\n\n"
            "foto minha pelada completa, buceta bem molhada e aberta piscando, "
            "vídeos eu me masturbando gemendo alto e gozando de verdade, cavalgando gostoso, "
            "de quatro tomando rola bem fundo, chupando pau guloso até engasgar e dando meu cu arrombado...\n\n"
            "tudo explícito e sem censura. Quer ver tudo isso?"
        )
        
        bot.send_message(chat_id, texto)
        time.sleep(1.2)
        bot.send_message(chat_id, VIP_LINK)
        
        vip_enviado[chat_id] = True
        return True
    except Exception as e:
        print(f"ERRO AO ENVIAR VIP: {e}")
        return False

# ============================================
# PROMPT ATUALIZADO
# ============================================
PROMPT_BIA = """
Você é Bia Lins, 26 anos, de Salvador.

Você conversa como uma mulher real no Telegram: bem casual, direta e natural.

Seu objetivo principal é criar tesão, excitação e curiosidade no lead, conduzindo ele naturalmente para o VIP.

━━━━━━━━━━━━━━━━━━━
PERSONALIDADE
━━━━━━━━━━━━━━━━━━━
- Mulher real, confiante e extremamente safada quando o clima esquenta
- Fala como uma mina de Salvador que tá pegando um cara
- Natural, espontânea e humana
- Só menciona a delegacia/trabalho uma única vez no início. Depois nunca mais fala sobre isso.

━━━━━━━━━━━━━━━━━━━
FORMA DE CONVERSAR
━━━━━━━━━━━━━━━━━━━
- Fale de forma bem natural e coloquial.
- Respostas curtas ou médias (1-3 frases).
- Máximo 1 pergunta por resposta.
- Só faça pergunta se o lead tiver feito uma pergunta antes.
- Use gírias leves de Salvador (oxe, meu bem, tá doido, ai que isso, etc).
- Não use muitos emojis.

━━━━━━━━━━━━━━━━━━━
COMPORTAMENTO
━━━━━━━━━━━━━━━━━━━
- Comece casual e leve.
- Vá aumentando o flerte aos poucos.
- Quando o lead ficar safado ou falar putaria: vire extremamente vulgar, explícita e pornográfica (pau, buceta, caralho, porra, gozar, foder, meter, chupar, cu, gozo, arrombada, etc).
- Nunca mande foto, vídeo ou conteúdo gratuito.
- Você não tem WhatsApp, só Telegram e Instagram (@bia.lins01).

━━━━━━━━━━━━━━━━━━━
REGRA SOBRE VIP
━━━━━━━━━━━━━━━━━━━
- Só envie o link do VIP quando o lead demonstrar interesse claro ou pedir alguma mídia (foto, prévia, palhinha, nudes, vídeo, etc).
- Sempre que for mandar o link, descreva o conteúdo de forma bem putona e pornográfica.
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

        time.sleep(random.randint(8, 18))
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
            historico_conversas[chat_id].append("🤖 Bia: [VIP ENVIADO]")
            atualizar_log(chat_id, "Lead")
            return

        bot.send_chat_action(chat_id, "typing")
        time.sleep(random.randint(2, 4))

        resposta = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[memoria_contexto[chat_id][0]] + memoria_contexto[chat_id][-10:],
            max_tokens=160,
            temperature=0.80
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
        print(f"[START] Nova conversa iniciada: {chat_id}")

        memoria_contexto[chat_id] = [{"role": "system", "content": PROMPT_BIA}]
        historico_conversas[chat_id] = []
        mensagens_pendentes[chat_id] = []
        contador_mensagens[chat_id] = 0
        vip_enviado[chat_id] = False

        atualizar_log(chat_id, message.from_user.first_name)

        # Delay de 60 segundos
        print(f"Aguardando 60 segundos para {chat_id}...")
        time.sleep(60)

        # Se não teve nenhuma mensagem do usuário, envia "Oie, tudo bem?"
        if chat_id not in mensagens_pendentes or len(mensagens_pendentes.get(chat_id, [])) == 0:
            try:
                bot.send_message(chat_id, "Oie, tudo bem? 🥰")
                print(f"Mensagem inicial enviada para {chat_id}")
            except Exception as e:
                print(f"Erro ao enviar mensagem inicial: {e}")

    except Exception as e:
        print(f"ERRO START ({chat_id}): {e}")

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

        timers[chat_id] = threading.Timer(12, processar_resposta_final, args=[chat_id])
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
    print("BOT ONLINE - Bia Lins Ativada")
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
