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
senha_api_news = os.getenv('senha_api_news')
senha_api_football = os.getenv('senha_api_football')

owm = pyowm.OWM(senha_api)
mgr = owm.weather_manager()

jogos_ao_vivo = [] 

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

def Ouvir():
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
    hora = datetime.datetime.now().hour
    comandos = await carregar_comandos()

    if 'adicionar comando' in comando:
        Falar('Ok, qual a pergunta?')
        pergunta = Ouvir()
        if pergunta:
            Falar('Pergunta gravada. Qual a resposta?')
            resposta = Ouvir()
            if resposta:
                await ensinar_luna(pergunta, resposta)
            else:
                Falar('Não consegui gravar a resposta.')
        else:
            Falar('Não consegui gravar a pergunta.')

    elif comando in comandos:
        Falar(comandos[comando])
   
    elif 'o que você pode fazer' in comando:
        Falar('Eu posso falar as horas, fazer pesquisas na Wikipédia e Google, abrir sites como Google, Instagram, Facebook, Spotify e Github, além de reproduzir músicas.')
    
    elif 'bom dia' in comando:
        if hora >= 0 and hora < 12:
            Falar('Bom dia! Espero que você tenha um dia maravilhoso! Estou aqui sempre pronta para te ajudar.')
        else:
            Falar('Não estamos no horario de bom dia, mas estou aqui para te ajudar.')

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

    
    elif 'jogos ao vivo' in comando:
        Falar('obtendo jogos ao vivo')
        await obter_jogos_ao_vivo()
        
        if jogos_ao_vivo:
          
          Falar("Aqui estão os jogos ao vivo:")
         
          for jogo in jogos_ao_vivo:
                
                Falar(f"{jogo['home_team']} {jogo['score_home']} x {jogo['away_team']} {jogo['score_away']} - Status: {jogo['status']}")
        else:
            Falar("Não há jogos ao vivo no momento.")

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
        for artigo in news['articles'][:2]:  # Limitar a 2 notícias
            Falar(f"Título: {artigo['title']}")
            Falar(f"{artigo['description']}\n")
   
    elif 'previsão do tempo em' in comando:
        cidade = comando.replace('previsão do tempo em', '').strip()
        Falar("Obtendo previsão do tempo em " + cidade)
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
        comando = Ouvir()
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
    Falar("Para Ouvir música diga toque nome do artista e música")
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
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={senha_api}&units=metric"
        resposta = requests.get(url)
        resposta.raise_for_status()  # Levanta um erro para códigos de status HTTP não 200
        
        dados = resposta.json()
        previsoes = dados['list'][:5]  # Limitar a 5 previsões (próximos 5 dias)

        Falar(f"Previsão do tempo para {cidade} nos próximos 5 dias:")
        for previsao in previsoes:
            data = datetime.datetime.fromtimestamp(previsao['dt'])
            temperatura_min = previsao['main']['temp_min']
            temperatura_max = previsao['main']['temp_max']
            descricao = traduzir_clima(previsao['weather'][0]['description'])
            Falar(f"Data: {data.strftime('%d/%m/%Y')}, Condição: {descricao}, Temperatura: entre {temperatura_min:.1f}°C e {temperatura_max:.1f}°C.")

    except requests.exceptions.HTTPError as e:
        Falar(f"Ocorreu um erro ao obter a previsão: {e}")
    except KeyError:
        Falar("Não consegui encontrar informações de previsão para a cidade especificada.")
    except Exception as e:
        Falar(f"Ocorreu um erro inesperado: {e}")

async def obter_jogos_ao_vivo():
    global jogos_ao_vivo
    url = "https://v3.football.api-sports.io/fixtures?live=all "
    headers = {
        'x-apisports-key': senha_api_football,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    try:
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status()
        dados = resposta.json()

        jogos_ao_vivo = []  # Limpa a lista antes de adicionar novos dados

        for jogo in dados['response']:
              if jogo['league']['country'] == 'Brazil':  # Filtra jogos no Brasil
               jogo_info = {
                'home_team': jogo['teams']['home']['name'],
                'away_team': jogo['teams']['away']['name'],
                'score_home': jogo['goals']['home'],
                'score_away': jogo['goals']['away'],
                'status': jogo['fixture']['status']['long']
            }
              jogos_ao_vivo.append(jogo_info)

    except requests.exceptions.HTTPError as e:
        Falar(f"Erro ao tentar ver todos os jogos ao vivo no Brasil: {e}")
if __name__ == "__main__":
   # asyncio.run(modo_apresentacao())
    asyncio.run(comando_voz_usuario())
