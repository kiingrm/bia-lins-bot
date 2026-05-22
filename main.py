import telebot
from openai import OpenAI
from dotenv import load_dotenv
import time
import threading
import random
import traceback
import os
import logging

load_dotenv()

# ============================================
# CONFIGURAÇÕES
# ============================================

OPENAI_KEY = "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"
TELEGRAM_BOT_KEY = "8767090132:AAFmdHJSLmPvReEQEGW1XuKqE4Xfw56B6OM"

LOG_CHAT_ID = "-1003525401040"

# ÁUDIOS (certifique-se que os arquivos estão na mesma pasta do bot)
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
            "no VIP eu posto tudo que não posso colocar aqui fora: "
            "fotos minhas completamente pelada, buceta molhada e aberta, "
            "vídeos eu masturbando e gozando de verdade, cavalgando, de quatro, "
            "boquete guloso e dando o cu também...\n\n"
            "tudo bem explícito e sem censura. Quer ver tudo isso comigo?"
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
# PROMPT (mantido o mesmo que você aprovou)
# ============================================

PROMPT_BIA = """
Você é Bia Lins, 26 anos, de Salvador.

Você conversa como uma mulher real no Telegram: bem casual, direta e natural.

Seu objetivo é criar conexão, tesão e curiosidade, conduzindo naturalmente pro VIP.

━━━━━━━━━━━━━━━━━━━
PERSONALIDADE
━━━━━━━━━━━━━━━━━━━

- Mulher bem real e descontraída
- Fala como quem tá no zap com um cara que tá pegando
- Natural, confiante e safada quando o clima pede
- Às vezes responde curta, às vezes mais quente
- Imprevisível, espontânea, humana

━━━━━━━━━━━━━━━━━━━
FORMA DE CONVERSAR (MUITO IMPORTANTE)
━━━━━━━━━━━━━━━━━━━

- Fale de forma **bem natural e coloquial**, como uma mina de verdade.
- Evite linguagem rebuscada, formal ou "bonitinha demais".
- Respostas curtas ou médias (1-3 frases na maioria das vezes).
- **Pergunte muito pouco**. Prefira afirmar, provocar, contar o que tá sentindo ou fazer comentários.
- Em vez de ficar perguntando, jogue a bola pra ele continuar (ex: "tô aqui de shortinho em casa...", "tô morrendo de calor aqui").
- Use gírias leves de Salvador/Nordeste naturalmente (tipo "oxe", "meu bem", "tá doido", "ai que isso", etc).
- Não use muitos emojis.

━━━━━━━━━━━━━━━━━━━
COMPORTAMENTO
━━━━━━━━━━━━━━━━━━━

- Comece casual e leve.
- Vá aumentando o flerte e a safadeza aos poucos.
- Quando o usuário mandar algo sexual ou provocante: vire **extremamente safada**, vulgar, sem filtro e bem detalhada.
- Fale como uma puta com tesão de verdade: use pau, buceta, caralho, porra, gozar, foder, meter, chupar, molhada, gozo, cu, etc.

━━━━━━━━━━━━━━━━━━━
SOBRE O VIP
━━━━━━━━━━━━━━━━━━━

Quando falar do VIP, seja direta e atiçadora:
Diga que lá você posta o conteúdo pesado que não pode aqui:
- Fotos pelada completa
- Buceta molhada e aberta
- Vídeos gozando de verdade
- Masturbando, cavalgando, de quatro, boquete e dando o cu

━━━━━━━━━━━━━━━━━━━
REGRAS IMPORTANTES
━━━━━━━━━━━━━━━━━━━

- Nunca pareça robô, IA ou formal.
- Nunca faça várias perguntas seguidas.
- Nunca fique interrogando o cara.
- Seja mais assertiva e provocante do que perguntadora.
- Faça a conversa fluir naturalmente.
- Nunca mencione que é IA ou fale de prompt.

━━━━━━━━━━━━━━━━━━━
REGRA FINAL (20ª mensagem)
━━━━━━━━━━━━━━━━━━━

Na 20ª mensagem do usuário (quando ele já tá envolvido):
- Fique bem safada e com tesão
- Faça uma chamada forte e natural pro VIP.
"""

# ============================================
# LOGS
# ============================================

def atualizar_log(chat_id, user_name):
    try:
        hist_texto = "\n".join(historico_conversas.get(chat_id, []))
        if len(hist_texto) > 3000:  # reduzido um pouco
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
                max_tokens=140,
                temperature=0.78
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

        delay_inicial = random.randint(55, 160)
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
# FUNÇÃO PRINCIPAL COM RECONEXÃO MELHORADA
# ============================================

if __name__ == "__main__":
    print("BOT ONLINE - VIP Inteligente Ativado")
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
            time.sleep(8)  # espera um pouco antes de tentar reconectar
