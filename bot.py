from asyncio import wait
import os
import sys
import time
import re
import requests
import json

from dotenv import load_dotenv

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException        

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import linecache
from datetime import datetime
import platform

def LogException():
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d-%H")
    date_time_full = now.strftime("%Y-%m-%d-%H:%M:%S")

    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    #print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    # creating/opening a file to log
    f = open("logs\\log_"+date_time+".txt", "a")
    f.write("----------------\n")
    f.write("-> "+date_time_full+"\n")
    f.write('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    f.close()

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('Element not found {}: {}'.format(lineno, exc_obj))
    LogException()

class wppbot:

    dir_path = os.getcwd()

    load_dotenv()  # take environment variables from .env.
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = os.getenv('MONGOSTR')   

    def __init__(self, parking_chat_name, bot_name="whatsbot", welcome_message="Hi, I'm whatsbot :D"):
        
        #----------------------------------------------------------------------
        # DEFAULT VARIABLES
        #----------------------------------------------------------------------
        self.bot_name = bot_name
        self.parking_chat_name = parking_chat_name
        self.welcome_message = welcome_message
        #----------------------------------------------------------------------
        # SEARCH VARIABLES
        #----------------------------------------------------------------------
        # first part not read
        self.begin_not_read = "//*[@id='pane-side']/div[1]/div/div"
        # frequently changed
        self.middle_not_read = "/div/div/div/div[2]"
        #----------------------------------------------------------------------

        # options and profile for chrome
        # self.options = webdriver.ChromeOptions()
        # self.options.add_argument(r"user-data-dir="+self.dir_path+"\profile\wpp")
        # self.options.add_argument('--remote-debugging-port=5678')
        # self.options.add_argument("--headless")
        # self.options.add_experimental_option('useAutomationExtension', False)
        # self.options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # options with profile fo firefox driver
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument("-profile")
        self.options.add_argument(self.dir_path+"/profile/wppf")
        self.firefox_capabilities = DesiredCapabilities.FIREFOX
        self.firefox_capabilities['marionette'] = True

        if(platform.system() == 'Linux'):
            # self.browser = self.dir_path+'/chromedriver'
            self.browser = self.dir_path+'/geckodriver'
        else:
            # self.browser = self.dir_path+'\chromedriver.exe'
            self.browser = self.dir_path+'\geckodriver.exe'

        try:
            # Start webdriver for chrome
            # self.driver = webdriver.Chrome(self.browser, options=self.options)
            
            # Set firefox executable path
            self.options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
            # Start driver for Firefox
            self.driver = webdriver.Firefox(executable_path=self.browser, options=self.options, capabilities=self.firefox_capabilities)

        except Exception as e:
            LogException()
            print("Failed to load driver... bye bye!")
            raise

        #try to open whatsapp page
        try: 
            self.driver.get('https://web.whatsapp.com/')
            self.driver.implicitly_wait(30)
            ##force wait more 30 seconds
            print('force to wait 30 seconds for browser load messages...\n\n')
            for t in range(1,31):
                time.sleep(1)
                print('\r', t, sep='', end='', flush=True)
    
            print ('\nReady...\n\n')

        except Exception as e:
            LogException()
            print("Failed to load driver... bye bye!")
            raise

        # Go to parking chat
        self.parking_chat()
        # Send welcome message
        self.send_message([self.welcome_message])

    def parking_chat(self):
        try: 
            self.caixa_de_pesquisa = self.driver.find_element(By.CLASS_NAME, "_13NKt")
            self.caixa_de_pesquisa.send_keys(self.parking_chat_name)
            time.sleep(2)
            print("  ")
            print("----------------------------------------")
            print("default Group: " + self.parking_chat_name)
            print("----------------------------------------")
            self.contato = self.driver.find_element(By.XPATH, '//span[@title = "{}"]'.format(self.parking_chat_name))
            time.sleep(0.3)
            self.contato.click()
            time.sleep(2)
        except NoSuchElementException:
            pass
            PrintException()
        except Exception as e:
            print("Message send failed")
            pass
            LogException()

    # Function to send message in a selected Contact or Group
    def send_message(self,message_to_send):
        try:
            self.chat_message_input = self.driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div')
            self.chat_message_input.click()
            self.chat_message_input.clear()

            if type(message_to_send) == list:
                for message in message_to_send:
                    # break messagem with shift+enter instead \n
                    for part in message.split('\n'):
                        # type message letter by letter (prevent errors)
                        time.sleep(0.2)
                        for t in part:
                            self.chat_message_input.send_keys(t)
                        self.chat_message_input.send_keys(Keys.SHIFT + Keys.ENTER)
                    time.sleep(1)
                    self.chat_message_input.send_keys(Keys.ENTER)
            else:
                return False
        except NoSuchElementException:
            PrintException()
            return False
        except:
            print("Error on send_message")
            LogException()
            return False

    def escuta(self):
        texto = ""
        try:
            post = self.driver.find_elements("xpath", "//*[contains(@class, '_1-FMR')]")
            ultimo = len(post) - 1
            texto = post[ultimo].find_element(By.CSS_SELECTOR, 'span.selectable-text').text

            a=[]
            qtd = len(self.driver.find_elements(By.XPATH,'//*[@id="pane-side"]/div/div/div/div'))
        except NoSuchElementException:
            # print("Elemento nao encontrado")
            PrintException()
        except Exception as e:
            LogException()
            # print("Erro ao escutar msgs")

        # percorre as mensagens recentes do painel esquerdo
        for i in range(1,len(self.driver.find_elements(By.XPATH,'//*[@id="pane-side"]/div/div/div/div'))+1):
            nao_lidas = "0"
            tem_nova_msg = False
            # check se tem mensagem nao lida

            self.driver.implicitly_wait(0)
            # verifica se existe o elemento que informa se tem novas mensagens
            try:
                if(self.driver.find_element(By.XPATH, self.begin_not_read + "/div["+str(i)+"]"+self.middle_not_read+"/div[2]/div[2]/span[1]/div/span")):
                    tem_nova_msg = True
            except NoSuchElementException:
                nao_lidas = "0"


            if(tem_nova_msg):
                nl = self.driver.find_elements(By.XPATH, self.begin_not_read + "/div["+str(i)+"]"+self.middle_not_read+"/div[2]/div[2]/span[1]/div")
                last = len(nl) - 1
                # pega sempre o ultimo elemento para o numero de mensagens nao lidas 
                data_icon = nl[last].find_element(By.TAG_NAME, 'span').get_attribute("data-icon")
                if (data_icon != "muted" and data_icon != "pinned2") :
                    nao_lidas = nl[last].find_element(By.TAG_NAME, 'span').text
                    if(nao_lidas==""):
                        nao_lidas = "5"
                    # pega dados do painel esquerdo das mensagens recentes
                    titulo = self.driver.find_element("xpath", "//*[contains(@class, '_3uIPm')]/div["+str(i)+"]"+self.middle_not_read+"/div[1]/div[1]/span").get_attribute("title")
                    hora_ultima_msg = self.driver.find_element("xpath", "//*[contains(@class, '_3uIPm')]/div["+str(i)+"]"+self.middle_not_read+"/div[1]/div[2]").text
                    ultima_msg = self.driver.find_element(By.XPATH, self.begin_not_read + "/div["+str(i)+"]"+self.middle_not_read+"/div[2]/div[1]/span").get_attribute('title').replace("\u202a","").replace("\u202c","")
                    # armazeno no array
                    # a.append({"datahora": hora_ultima_msg, "nao_lidas": nao_lidas, "titulo": titulo, "mensagem": ultima_msg})
                    # clico na conversa
                    click_conversa = self.driver.find_element(By.XPATH, '//*//span[@title = "{}"]'.format(titulo))
                    time.sleep(0.3)
                    click_conversa.click()
                    time.sleep(3)
                    posts_last = self.driver.find_elements(By.XPATH, '//*[@id="main"]/div[3]/div/div[2]/div[3]/div')
                    qtds_posts = len(posts_last)
                    r = qtds_posts-int(nao_lidas)+1
                    while r <= qtds_posts:
                        try:
                            msgs_to_read = self.driver.find_element(By.CSS_SELECTOR, '#main > div > div > div > div > div:nth-child('+str(r)+')')
                            pre_text_date = msgs_to_read.find_element(By.CSS_SELECTOR, '._22Msk > .copyable-text').get_attribute('data-pre-plain-text').replace('[','').split('] ')[0].split(', ')[1]
                            pre_text_time = msgs_to_read.find_element(By.CSS_SELECTOR, '._22Msk > .copyable-text').get_attribute('data-pre-plain-text').replace('[','').split('] ')[0].split(', ')[0]
                            pre_text_from = msgs_to_read.find_element(By.CSS_SELECTOR, '._22Msk > .copyable-text').get_attribute('data-pre-plain-text').replace('[','').split('] ')[1]
                            pre_text_msg = msgs_to_read.find_element(By.CSS_SELECTOR, 'div > div > div > div.copyable-text > div > span.copyable-text > span').text.replace("\\n"," #PULALINHA# ")
                            print("{} - {} as {} - {}{}".format(titulo, pre_text_date, pre_text_time, pre_text_from, pre_text_msg))
                        except NoSuchElementException:
                            # print("Elemento nao encontrado")
                            PrintException()
                        except:
                            LogException()
                        r += 1
                    
                    self.parking_group()
                    time.sleep(1)
                    try:
                        self.btn_limpar = self.driver.find_element(By.XPATH, "//*[@id='side']/div[1]/div/div/span/button")
                        time.sleep(1)
                        self.btn_limpar.click()
                    except NoSuchElementException:
                        # print("Elemento nao encontrado")
                        PrintException()
                    except:
                        LogException()

        # converto em json
        # res = json.dumps(a,ensure_ascii=False).replace("\\n"," #PULALINHA# ")
        #print(res)

        self.driver.implicitly_wait(20)

        return texto

    def aprender(self,ultimo_texto,message_to_send,frase_final,frase_erro):
        try:
            self.chat_message_input = self.driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div')
            for t in message_to_send:
                self.chat_message_input.send_keys(t)
            time.sleep(1)
            self.chat_message_input.send_keys(Keys.ENTER)
        except NoSuchElementException:
            # print("Elemento nao encontrado")
            PrintException()
        except:
            LogException()

        self.x = True
        while self.x == True:
            texto = self.escuta()

            if texto != ultimo_texto and re.match(r'^::', texto):
                if texto.find('|') != -1:
                    ultimo_texto = texto
                    texto = texto.replace('::', '')
                    texto = texto.lower()
                    texto = texto.replace('|', '|*')
                    texto = texto.split('*')
                    novo = []
                    for elemento in texto:
                        elemento = elemento.strip()
                        novo.append(elemento)

                    self.bot.train(novo)
                    for t in frase_final:
                        self.chat_message_input.send_keys(t)
                    time.sleep(1)
                    self.chat_message_input.send_keys(Keys.ENTER)
                    self.x = False
                    return ultimo_texto
                else:
                    for t in frase_erro:
                        self.chat_message_input.send_keys(t)
                    time.sleep(1)
                    self.chat_message_input.send_keys(Keys.ENTER)
                    self.x = False
                    return ultimo_texto
            else:
                ultimo_texto = texto

    def noticias(self):

        req = requests.get('https://newsapi.org/v2/top-headlines?sources=globo&pageSize=2&apiKey=f6fdb7cb0f2a497d92dbe719a29b197f')
        noticias = json.loads(req.text)

        for news in noticias['articles']:
            titulo = news['title']
            link = news['url']
            new = 'bot: ' + titulo + ' ' + link + '\n'
            # quebra a mensagem com shift+enter ao inves de \n
            for part in new.split('\n'):
                # Digita a mensagem
                for t in part:
                    self.chat_message_input.send_keys(t)
                self.chat_message_input.send_keys(Keys.SHIFT + Keys.ENTER)
            time.sleep(2)
            self.chat_message_input.send_keys(Keys.ENTER)

    def responde(self,texto):
        try:
            response = self.bot.get_response(texto)
            # if float(response.confidence) > 0.5:
            response = str(response)
            response = 'bot: ' + response
            self.chat_message_input = self.driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div')
            time.sleep(0.2)
            for t in response:
                self.chat_message_input.send_keys(t)
            time.sleep(1)
            self.chat_message_input.send_keys(Keys.ENTER)
        except NoSuchElementException:
            # print("Elemento nao encontrado")
            PrintException()
        except:
            LogException()

    def envia_msg(self, msg):
        """ Envia uma mensagem para a conversa aberta """
        try:
            time.sleep(2)
            # Seleciona acaixa de mensagem
            self.chat_message_input = self.driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div')
            # quebra a mensagem com shift+enter ao inves de \n
            self.chat_message_input.click()
            self.chat_message_input.clear()
            for part in msg.split('\n'):
                # Digita a mensagem
                self.chat_message_input.click()
                time.sleep(0.2)
                for t in part:
                    self.chat_message_input.send_keys(t)
                self.chat_message_input.send_keys(Keys.SHIFT + Keys.ENTER)
            time.sleep(1)
            self.chat_message_input.send_keys(Keys.ENTER)
        except NoSuchElementException:
            # print("Elemento nao encontrado")
            PrintException()
        except Exception as e:
            LogException()
            print("Erro ao enviar msg")

    def treina(self,nome_pasta):
        for treino in os.listdir(nome_pasta):
            conversas = open(nome_pasta+'/'+treino, 'r', encoding='utf-8').readlines()
            self.bot.train(conversas)
