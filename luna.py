import speech_recognition as sr
from gtts import gTTS
import datetime
import wikipedia
import os
import pygame
import time
import webbrowser
import pywhatkit as kit
import pyowm
import threading
import asyncio
import json
from dotenv import load_dotenv
import requests

# Inicializa o reconhecedor de voz e o mixer do pygame
audio = sr.Recognizer()
pygame.mixer.init()

load_dotenv()
senha_api = os.getenv('senha_api_tempo')
owm = pyowm.OWM(senha_api)
mgr = owm.weather_manager()
senha_api_news = os.getenv('senha_api_news')

silencio = False

def Falar(texto):
    global silencio
    if silencio:
        return
    print("Luna: " + texto)
    arquivo_audio = "resposta.mp3"

    tts = gTTS(text=texto, lang='pt-br')
    tts.save(arquivo_audio)

    pygame.mixer.music.load(arquivo_audio)
    pygame.mixer.music.play()

    # Aguardar até a reprodução terminar
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)  # Reduz o tempo de espera ativo

    pygame.mixer.music.unload()

    if os.path.exists(arquivo_audio):
        try:
            os.remove(arquivo_audio)
        except PermissionError:
            print(f"Erro ao tentar remover o arquivo {arquivo_audio}. Arquivo está em uso.")
        except Exception as e:
            print(f"Ocorreu um erro ao tentar remover o arquivo {arquivo_audio}: {e}")

def ouvir():
    with sr.Microphone() as source:
        try:
            audio.adjust_for_ambient_noise(source)  # Ajusta para o ruído ambiente
            print("Estou ouvindo, fale algo")
            voz = audio.listen(source)
            comando = audio.recognize_google(voz, language='pt-BR')
            print("O usuário disse: " + comando)
            return comando.lower()  # Retorna o comando em minúsculas
        except sr.UnknownValueError:
            print("Não consegui entender o áudio.")
            Falar("Desculpe, não consegui entender o que você disse.")
            return None
        except sr.RequestError:
            print("Erro ao se conectar ao serviço de reconhecimento de voz.")
            Falar("Houve um problema com o serviço de reconhecimento de voz.")
            return None
        except Exception as e:
            print("Ocorreu um erro:", e)
            Falar("Ocorreu um erro inesperado.")
            return None

async def carregar_comandos(arquivo='comandos.json'):
    try:
        with open(arquivo, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Arquivo não encontrado.")
        return {}
    except json.JSONDecodeError:
        print("Erro ao decodificar o JSON.")
        return {}

async def salvar_comandos(comandos, arquivo='comandos.json'):
    with open(arquivo, 'w') as f:
        json.dump(comandos, f, ensure_ascii=False, indent=4)

async def ensinar_luna(pergunta, resposta):
    comandos = await carregar_comandos()
    comandos[pergunta] = resposta
    await salvar_comandos(comandos)
    Falar("Aprendi algo novo!")

async def sites(url):
    urls = {
        "google": "https://www.google.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "spotify": "https://open.spotify.com/intl-pt",
        "github": "https://www.github.com"
    }
    
    if url in urls:
        Falar(f"Abrindo {url} agora...")
        webbrowser.open(urls[url])
    else:
        Falar(f"Desculpe, não sei como abrir {url}.")

def traduzir_clima(descricao):
    traducoes = {
        "clear sky": "céu limpo",
        "few clouds": "poucas nuvens",
        "scattered clouds": "nuvens dispersas",
        "broken clouds": "nuvens quebradas",
        "overcast clouds": "nublado",
        "shower rain": "chuva de banho",
        "rain": "chuva",
        "thunderstorm": "trovoada",
        "snow": "neve",
        "mist": "névoa"
    }
    return traducoes.get(descricao, descricao)

async def executar_comando(comando):
    global silencio
    comandos = await carregar_comandos()

    if 'me ensine sobre' in comando:
        partes = comando.replace('me ensine sobre', '').split('a resposta é')
        if len(partes) == 2:
            pergunta = partes[0].strip()
            resposta = partes[1].strip()
            await ensinar_luna(pergunta, resposta)
       
        else:
            Falar("Por favor, use o formato: me ensine sobre [pergunta], a resposta é [resposta]")
    
    elif comando in comandos:
        Falar(comandos[comando])
   
    elif 'o que você pode fazer' in comando:
        Falar('Eu posso falar as horas, fazer pesquisas na Wikipédia e Google, abrir sites como Google, Instagram, Facebook, Spotify e Github, além de reproduzir músicas.')
    
    elif 'horas são' in comando:
        horas = datetime.datetime.now().strftime('%H:%M')
        Falar("Agora são " + horas)
    
    elif 'me diga sobre' in comando or 'me fale sobre' in comando:
        sobre = comando.replace('me diga sobre', '').replace('me fale sobre', '').strip()
        wikipedia.set_lang('pt')
        try:
            Falar("Procurando sobre " + sobre)
            resposta = wikipedia.summary(sobre, sentences=2)
            Falar(resposta)
        except wikipedia.exceptions.DisambiguationError:
            Falar("A pesquisa retornou múltiplas opções. Por favor, seja mais específico.")
    
    elif 'abra o' in comando:
        site = comando.replace('abra o', '').strip()
        await sites(site)
   
    elif 'toque' in comando:
        toque = comando.replace('toque', '').strip()
        Falar('Tocando ' + toque)
        threading.Thread(target=kit.playonyt, args=(toque,)).start()  # Executa em uma nova thread
   
    elif 'qual a temperatura em' in comando:
        cidade = comando.replace('qual a temperatura em', '').strip()
        Falar('Obtendo informações do clima em ' + cidade)
        try:
            observacao = mgr.weather_at_place(cidade)
            clima = observacao.weather
            temperatura = clima.temperature('celsius')['temp']
            descricao = traduzir_clima(clima.detailed_status)
            Falar(f'Em {cidade} a temperatura é {temperatura:.1f}°C e o tempo está {descricao}.')
        except pyowm.commons.exceptions.NotFoundError:
            Falar(f"Não consegui encontrar informações climáticas para {cidade}.")
  
    elif 'procure por' in comando:
        pesquisa = comando.replace('procure por', '').strip()
        Falar('Procurando no Google por ' + pesquisa)
        threading.Thread(target=kit.search, args=(pesquisa,)).start()  # Executa em uma nova thread
   
    elif 'sair' in comando or 'encerrar' in comando:
        Falar("Encerrando o assistente. Até logo!")
        exit()
   
    elif 'pare de falar' in comando or 'silêncio' in comando:
        silencio = True
        Falar("Entrando em modo silencioso.")
    
    elif 'fim do silêncio' in comando:
        silencio = False
        Falar("Saindo do modo silencioso.")
   
    elif 'desligar computador' in comando:
        Falar('Seu computador será desligado em 30 segundos. Você pode cancelar o desligamento dizendo "cancelar desligamento".')
        os.system("shutdown /s /t 30")  # Comando para desligar em 30 segundos
 
    elif 'notícias de' in comando:
        noticias = comando.replace('notícias de', '').strip()
        Falar('Procurando por notícias de ' + noticias)
        news = await news_api(noticias)  
        for artigo in news['articles'] [:2]:# limiar a 2 noticias
            Falar(f"Título: {artigo['title']}")
            Falar(f"{artigo['description']}\n")
   
    elif 'previsão do tempo em ' in comando:
        cidade = comando.replace('previsão do tempo em','').strip()
        Falar("Obtendo previsão do tempo em "+ cidade)
        await obter_previsao(cidade)


    elif 'cancelar desligamento' in comando:
        os.system("shutdown /a")  # Comando para abortar o desligamento
        Falar("Desligamento cancelado.")
    elif 'reiniciar computador' in comando:
        Falar('Seu computador será reiniciado em 30 segundos. Você pode cancelar o reinício dizendo "cancelar reinício".')
        os.system("shutdown /r /t 30")  # Comando para reiniciar em 30 segundos
    elif 'cancelar reinício' in comando:
        os.system("shutdown /a")  # Comando para abortar o reinício
        Falar("Reinício cancelado.")
    else:
        Falar("Comando não reconhecido.")

async def comando_voz_usuario():
    while True:
        comando = ouvir()
        if comando and 'luna' in comando:
            comando = comando.replace('luna', '').strip()
            await executar_comando(comando)
        else:
            Falar("Você não me chamou pelo nome.")

async def modo_apresentacao():
    Falar("Olá, eu sou a Luna, sua assistente virtual. Aqui está o que eu posso fazer:")
    time.sleep(1)
    Falar("Posso falar as horas, fazer pesquisas na Wikipédia e Google, abrir sites como Google, Instagram, Facebook, Spotify e Github, além de reproduzir músicas.")
    time.sleep(1)
    Falar("Para ouvir música diga toque nome do artista e música")
    time.sleep(1)
    Falar("Posso também informar a temperatura em qualquer cidade do mundo, além de aprender novos comandos que você me ensinar.")
    time.sleep(1)
    Falar("Para ativar um comando, basta dizer 'Luna' seguido do comando desejado.")
    time.sleep(1)
    Falar("Como posso te ajudar hoje?")

async def news_api(termo_pesquisa):
    url = f'https://newsapi.org/v2/everything?q={termo_pesquisa}&apiKey={senha_api_news}'
    resposta = requests.get(url)
    return resposta.json()  

async def obter_previsao(cidade):
    try:
        previsao = mgr.forecast_at_place(cidade, '5d').forecast
        previsoes = previsao.weathers

        Falar(f"Previsão do tempo para {cidade} nos próximos 5 dias:")
        for weather in previsoes:
            dados = weather.reference_time('date')
            temperatura = weather.temperature('celsius')['day']
            descricao = traduzir_clima(weather.detailed_status)
            Falar(f"Data: {dados.strftime('%d/%m/%Y')}, Temperatura: {temperatura:.1f}°C, Condição: {descricao}")

    except pyowm.commons.exceptions.NotFoundError:
        Falar(f"Não consegui encontrar informações climáticas para {cidade}.")
    

if __name__ == "__main__":
   # asyncio.run(modo_apresentacao())
    asyncio.run(comando_voz_usuario())
