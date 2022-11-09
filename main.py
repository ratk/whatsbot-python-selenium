import re
import time
from bot import wppbot

bot_name = "Geobot"
parking_chat_name = "Grupo Repouso Bot Python"
welcome_message = "*--------*\nBot: Oi, sou o "+bot_name+"!\nBot: Use *::* no início para falar comigo"

# Start class whatsbot and open browser for start
bot = wppbot(parking_chat_name, bot_name, welcome_message)

ultimo_texto = ''
texto = ""

# while texto != "/quit":
#     time.sleep(5)
#     texto = bot.escuta()

#     if texto == '/quit':
#         bot.envia_msg("bot: Bye bye!")
#         bot.send_message("bot: Bye bye!")
#         time.sleep(4)
#     elif texto != ultimo_texto and re.match(r'^::', texto):
#         ultimo_texto = texto
#         texto = texto.replace('::', '')
#         texto = texto.lower()

#         if (texto == 'aprender' or texto == ' aprender' or texto == 'ensinar' or texto == ' ensinar'):
#             bot.aprender(texto,'bot: Escreva a pergunta e após o | a resposta.','bot: Obrigado por ensinar! Agora já sei!','bot: Você escreveu algo errado! Comece novamente..')
#         elif (texto == 'noticias' or texto == ' noticias' or texto == 'noticia' or texto == ' noticia' or texto == 'notícias' or texto == ' notícias' or texto == 'notícia' or texto == ' notícia'):
#             bot.noticias()
#         else:
#             bot.responde(texto)

bot.driver.close()
bot.driver.quit()
exit()
