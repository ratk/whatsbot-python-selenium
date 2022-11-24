import re
import time
from bot import wppbot

bot_name = "Geobot"
parking_chat_name = "Grupo Repouso Bot Python"
welcome_message = "*--------*\nBot: Oi, sou o "+bot_name+"!\nBot: Use *::* no início para falar comigo"

# Start class whatsbot and open browser for start
bot = wppbot(parking_chat_name, bot_name, welcome_message)

last_msg = ''
message = ""

while message != "/quit":
    time.sleep(5)
    message = bot.parking_group_listner()

    if message != last_msg and re.match(r'^::', message):
        last_msg = message
        message = message.replace('::', '')
        message = message.lower()
    
    # If empty search for new msgs
    if message != "/quit":
        bot.parking_default_listner()

# ---------------------------
# End of program
# ---------------------------

for t in range(1,6):
    print('\rLeaving in ', 6-t, sep='', end='', flush=True)
    time.sleep(1)

# Go to parking chat and send close msg
bot.parking_chat()
bot.send_message("bot: Bye bye!")
print("\n\nbot: Bye bye!")

#close driver and quit
bot.driver.close()
bot.driver.quit()

exit()
