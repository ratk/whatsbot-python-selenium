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

from spacy.cli import download
import linecache
from datetime import datetime


#download("en_core_web_sm")

def PrintException():
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d-%H")

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
    f.write('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    f.close()

class ENGSM: 
    ISO_639_1 = 'en_core_web_sm'

class wppbot:

    dir_path = os.getcwd()

    load_dotenv()  # take environment variables from .env.
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = os.getenv('MONGOSTR')   

    def __init__(self, nome_bot):
        print(self.dir_path)
        self.bot = ChatBot(nome_bot, 
            storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.BestMatch',
                    'default_response': 'I am sorry, but I do not understand.'
                }
            ],
            database_uri=self.CONNECTION_STRING,
            tagger_language=ENGSM
        )
        
        #----------------------------------------------------------------------
        # SEARCH VARIABLES
        #----------------------------------------------------------------------
        # first part not read
        self.not_read_inicio = "//*[@id='pane-side']/div[1]/div/div"
        # frequently changed
        self.not_read_meio = "/div/div/div/div[2]"
        #----------------------------------------------------------------------

        # self.trainer = ListTrainer(self.bot)
        self.bot.set_trainer(ListTrainer)

        self.chrome = self.dir_path+'\chromedriver.exe'

        self.options = webdriver.ChromeOptions()
        self.options.add_argument(r"user-data-dir="+self.dir_path+"\profile\wpp")
        self.options.add_argument('--remote-debugging-port=5678')
        
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Inicializa o webdriver
        self.driver = webdriver.Chrome(self.chrome, options=self.options)
    

    def inicia(self,nome_contato):
        try: 
            self.driver.get('https://web.whatsapp.com/')
            self.driver.implicitly_wait(20)
            ##force wait more 20 seconds
            print('aguardando 20 segundos para mensagens do chrome')
            time.sleep(20)
            print ('continuando\n\n')

            self.caixa_de_pesquisa = self.driver.find_element(By.CLASS_NAME, "_13NKt")

            self.caixa_de_pesquisa.send_keys(nome_contato)
            time.sleep(2)
            print(nome_contato)
            self.contato = self.driver.find_element(By.XPATH, '//span[@title = "{}"]'.format(nome_contato))
            self.contato.click()
            time.sleep(2)
        except webdriver.common.exception.NoSuchElementException:
            print("Elemento nao encontrado")
            PrintException()
            pass
        except Exception as e:
            PrintException()
            print("Erro ao enviar msg")
            pass


    def saudacao(self,frase_inicial):
        self.caixa_de_mensagem = self.driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div')

        if type(frase_inicial) == list:
            for frase in frase_inicial:
                # quebra a mensagem com shift+enter ao inves de \n
                for part in frase.split('\n'):
                    # Digita a mensagem
                    self.caixa_de_mensagem.send_keys(part)
                    self.caixa_de_mensagem.send_keys(Keys.SHIFT + Keys.ENTER)
                time.sleep(1)
                self.caixa_de_mensagem.send_keys(Keys.ENTER)
        else:
            return False

    def escuta(self):
        texto = ""
        try:
            post = self.driver.find_elements("xpath", "//*[contains(@class, '_1-FMR')]")
            ultimo = len(post) - 1
            texto = post[ultimo].find_element(By.CSS_SELECTOR, 'span.selectable-text').text

            a=[]
            qtd = len(self.driver.find_elements(By.XPATH,'//*[@id="pane-side"]/div/div/div/div'))
        except Exception as e:
            PrintException()
            # print("Erro ao escutar msgs")

        # percorre as mensagens recentes do painel esquerdo
        for i in range(1,len(self.driver.find_elements(By.XPATH,'//*[@id="pane-side"]/div/div/div/div'))+1):
            nao_lidas = "0"
            tem_nova_msg = False
            # check se tem mensagem nao lida

            self.driver.implicitly_wait(0)
            # verifica se existe o elemento que informa se tem novas mensagens
            try:
                if(self.driver.find_element(By.XPATH, self.not_read_inicio + "/div["+str(i)+"]"+self.not_read_meio+"/div[2]/div[2]/span[1]/div/span")):
                    tem_nova_msg = True
            except NoSuchElementException:
                nao_lidas = "0"


            if(tem_nova_msg):
                nl = self.driver.find_elements(By.XPATH, self.not_read_inicio + "/div["+str(i)+"]"+self.not_read_meio+"/div[2]/div[2]/span[1]/div")
                last = len(nl) - 1
                # pega sempre o ultimo elemento para o numero de mensagens nao lidas 
                data_icon = nl[last].find_element(By.TAG_NAME, 'span').get_attribute("data-icon")
                if (data_icon != "muted" and data_icon != "pinned2") :
                    nao_lidas = nl[last].find_element(By.TAG_NAME, 'span').text
                    if(nao_lidas==""):
                        nao_lidas = "3"
                    # pega dados do painel esquerdo das mensagens recentes
                    titulo = self.driver.find_element("xpath", "//*[contains(@class, '_3uIPm')]/div["+str(i)+"]"+self.not_read_meio+"/div[1]/div[1]/span").get_attribute("title")
                    hora_ultima_msg = self.driver.find_element("xpath", "//*[contains(@class, '_3uIPm')]/div["+str(i)+"]"+self.not_read_meio+"/div[1]/div[2]").text
                    ultima_msg = self.driver.find_element(By.XPATH, self.not_read_inicio + "/div["+str(i)+"]"+self.not_read_meio+"/div[2]/div[1]/span").get_attribute('title').replace("\u202a","").replace("\u202c","")
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
                        except:
                            PrintException()
                        r += 1
        # converto em json
        # res = json.dumps(a,ensure_ascii=False).replace("\\n"," #PULALINHA# ")
        #print(res)

        self.driver.implicitly_wait(20)

        return texto

    def aprender(self,ultimo_texto,frase_inicial,frase_final,frase_erro):
        self.caixa_de_mensagem = self.driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div')
        self.caixa_de_mensagem.send_keys(frase_inicial)
        time.sleep(1)
        self.caixa_de_mensagem.send_keys(Keys.ENTER)
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
                    self.caixa_de_mensagem.send_keys(frase_final)
                    time.sleep(1)
                    self.caixa_de_mensagem.send_keys(Keys.ENTER)
                    self.x = False
                    return ultimo_texto
                else:
                    self.caixa_de_mensagem.send_keys(frase_erro)
                    time.sleep(1)
                    self.caixa_de_mensagem.send_keys(Keys.ENTER)
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
                self.caixa_de_mensagem.send_keys(part)
                self.caixa_de_mensagem.send_keys(Keys.SHIFT + Keys.ENTER)
            time.sleep(2)
            self.caixa_de_mensagem.send_keys(Keys.ENTER)

    def responde(self,texto):
        response = self.bot.get_response(texto)
        # if float(response.confidence) > 0.5:
        response = str(response)
        response = 'bot: ' + response
        self.caixa_de_mensagem = self.driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div')
        self.caixa_de_mensagem.send_keys(response)
        time.sleep(1)
        self.caixa_de_mensagem.send_keys(Keys.ENTER)

    def envia_msg(self, msg):
        """ Envia uma mensagem para a conversa aberta """
        try:
            time.sleep(2)
            # Seleciona acaixa de mensagem
            self.caixa_de_mensagem = self.driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div')
            # quebra a mensagem com shift+enter ao inves de \n
            for part in msg.split('\n'):
                # Digita a mensagem
                self.caixa_de_mensagem.send_keys(part)
                self.caixa_de_mensagem.send_keys(Keys.SHIFT + Keys.ENTER)
            time.sleep(1)
            self.caixa_de_mensagem.send_keys(Keys.ENTER)
        except webdriver.common.exception.NoSuchElementException:
            print("Elemento nao encontrado")
            PrintException()
        except Exception as e:
            PrintException()
            print("Erro ao enviar msg")

    def treina(self,nome_pasta):
        for treino in os.listdir(nome_pasta):
            conversas = open(nome_pasta+'/'+treino, 'r', encoding='utf-8').readlines()
            self.bot.train(conversas)
