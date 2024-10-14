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

# Inicializa o reconhecedor de voz e o mixer do pygame
audio = sr.Recognizer()
pygame.mixer.init()

# Substitua pela sua chave de API do OpenWeatherMap
owm = pyowm.OWM('166936b11d98f4fc3e044f70dd6fa985')
mgr = owm.weather_manager()
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

    # Certificar-se de que a música não está mais sendo reproduzida antes de remover
    pygame.mixer.music.unload()

    # Verificar se o arquivo existe antes de tentar removê-lo
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

async def carregar_comandos(aquivo='comandos.json'):
    try:
        with open(aquivo, 'r') as f:
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
        if 'me diga sobre' in comando:
            sobre = comando.replace('me diga sobre', '').strip()
        else:
            sobre = comando.replace('me fale sobre', '').strip()
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
    elif 'luna' in comando or 'fim do silêncio' in comando:
        silencio = False
        Falar("Saindo do modo silencioso.")
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

if __name__ == "__main__":
    asyncio.run(comando_voz_usuario())
