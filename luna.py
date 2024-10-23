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
import pytz
from dateutil import parser


audio = sr.Recognizer()
pygame.mixer.init()

load_dotenv()

senha_api = os.getenv('senha_api_tempo')
senha_api_news = os.getenv('senha_api_news')
senha_api_football = os.getenv('senha_api_football')

owm = pyowm.OWM(senha_api)
mgr = owm.weather_manager()

jogos_ao_vivo = []
jogos_hoje = []
silencio = False

campeonatos_famosos = [
    "Brasileirão Série A", "Copa Libertadores", "Copa do Brasil", "Copa Sul-Americana",
    "Champions League", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"
]

times_brasileiros = ["Flamengo", "Palmeiras", "São Paulo", "Santos", "Corinthians", "Grêmio", 
                     "Internacional", "Atlético Mineiro", "Cruzeiro", "Fluminense", "Botafogo", 
                     "Vasco da Gama", "Bahia", "Sport Recife", "Ceará", "Fortaleza"]

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

   
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)  

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
            audio.adjust_for_ambient_noise(source) 
            print("Estou ouvindo, fale algo")
            voz = audio.listen(source)
            comando = audio.recognize_google(voz, language='pt-BR')
            print("O usuário disse: " + comando)
            return comando.lower()  
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

def criar_pasta(nome_pasta):
    area_de_trabalho = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    caminho_pasta = os.path.join(area_de_trabalho, nome_pasta)

    try:
        os.makedirs(caminho_pasta, exist_ok=True)
        Falar(f"Pasta {nome_pasta} criada com sucesso na área de trabalho.")
    except Exception as e:
        Falar(f"Ocorreu um erro ao criar a pasta: {e}")

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
            Falar('Não estamos no horário de bom dia, mas estou aqui para te ajudar.')

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
        threading.Thread(target=kit.playonyt, args=(toque,)).start()
   
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
        threading.Thread(target=kit.search, args=(pesquisa,)).start() 

    elif 'notícias de hoje' in comando:
        Falar('Obtendo as últimas notícias...')
        url = f'https://newsapi.org/v2/top-headlines?country=br&apiKey={senha_api_news}'
        response = requests.get(url)
        noticias = response.json()
        if noticias['status'] == 'ok':
            for i, noticia in enumerate(noticias['articles'][:5], start=1):
                Falar(f"Notícia {i}: {noticia['title']}")
        else:
            Falar('Não consegui obter as notícias no momento.')
   
    elif 'desligue o microfone' in comando or 'fique em silêncio' in comando:
        silencio = True
        Falar("Ok, ficarei em silêncio.")
    
    elif 'volte a falar' in comando or 'pode falar' in comando:
        silencio = False
        Falar("Ok, voltarei a falar.")
   
    elif 'criar pasta' in comando:
        Falar("Qual o nome da pasta?")
        nome_pasta = Ouvir()
        if nome_pasta:
            criar_pasta(nome_pasta)
        else:
            Falar("Não consegui entender o nome da pasta.")
   
    else:
        Falar("Desculpe, não entendi o comando. Você pode repetir?")

async def obter_jogos_ao_vivo():
    global jogos_ao_vivo
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {
        'x-apisports-key': senha_api_football
    }
    response = requests.get(url, headers=headers)
   
    if response.status_code == 200:
        data = response.json()
        jogos_ao_vivo = [
            {
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'score_home': fixture['goals']['home'],
                'score_away': fixture['goals']['away'],
                'status': fixture['fixture']['status']['short']
            }
            for fixture in data['response']
        ]
    else:
        Falar("Não consegui obter os jogos ao vivo no momento.")

def formatar_horario_iso(iso_str):
    try:
        dt = parser.parse(iso_str)
        dt = dt.astimezone(pytz.timezone('America/Sao_Paulo'))
        return dt.strftime('%H:%M')
    except Exception as e:
        print(f"Erro ao formatar o horário: {e}")
        return "Hora desconhecida"

async def obter_jogos_hoje():
    global jogos_hoje
    hoje = datetime.datetime.now().strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    headers = {
        'x-apisports-key': senha_api_football
    }
    response = requests.get(url, headers=headers)
   
    if response.status_code == 200:
        data = response.json()
        jogos_hoje = [
            {
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'time': formatar_horario_iso(fixture['fixture']['date']),
                'league': fixture['league']['name']
            }
            for fixture in data['response']
            if (fixture['league']['name'] in campeonatos_famosos or 
                fixture['teams']['home']['name'] in times_brasileiros or 
                fixture['teams']['away']['name'] in times_brasileiros)
        ]
       
        if jogos_hoje:
            Falar("Aqui estão os jogos programados para hoje:")
            for jogo in jogos_hoje:
                Falar(f"{jogo['home_team']} x {jogo['away_team']} - Hora: {jogo['time']} - Campeonato: {jogo['league']}")
        else:
            Falar("Não há jogos programados para hoje.")
    else:
        Falar("Não consegui obter os jogos de hoje no momento.")

async def main():
    while True:
        comando = Ouvir()
        if comando and 'luna' in comando:
            comando = comando.replace('luna', '').strip()
            await executar_comando(comando)
        else:
            Falar('Você não me chamou pelo nome')

if __name__ == "__main__":
    asyncio.run(main())
