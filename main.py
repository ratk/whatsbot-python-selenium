import re
from bot import wppbot
import sys
import time

botName = "Geobot"
default_chat = "Teste Bot Whats"

bot = wppbot(botName)
bot.treina('treinamento')
bot.iniciadriver()
bot.inicio(default_chat)

bot.saudacao(['*--------*\nBot: Oi, sou o '+botName+'!\nBot: Use *::* no início para falar comigo'])
# bot.send_message("bot: OIIIII!")

ultimo_texto = ''
texto = ""

while texto != "/quit":
    time.sleep(5)
    texto = bot.escuta()

    if texto == '/quit':
        bot.envia_msg("bot: Bye bye!")
        bot.send_message("bot: Bye bye!")
        time.sleep(4)
    elif texto != ultimo_texto and re.match(r'^::', texto):
        ultimo_texto = texto
        texto = texto.replace('::', '')
        texto = texto.lower()

        if (texto == 'aprender' or texto == ' aprender' or texto == 'ensinar' or texto == ' ensinar'):
            bot.aprender(texto,'bot: Escreva a pergunta e após o | a resposta.','bot: Obrigado por ensinar! Agora já sei!','bot: Você escreveu algo errado! Comece novamente..')
        elif (texto == 'noticias' or texto == ' noticias' or texto == 'noticia' or texto == ' noticia' or texto == 'notícias' or texto == ' notícias' or texto == 'notícia' or texto == ' notícia'):
            bot.noticias()
        else:
            bot.responde(texto)

bot.driver.close()
bot.driver.quit()
exit()
