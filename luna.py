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
    print(texto)  # Para visualizar o que está sendo dito
    arquivo_audio = f"resposta_{int(time.time())}.mp3"  # Nome único baseado no timestamp

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

def reconhecer_comando():
    """Reconhece o comando de voz do usuário."""
    with sr.Microphone() as source:
        try:
            audio.adjust_for_ambient_noise(source)  # Ajusta para o ruído ambiente
            Falar("Estou ouvindo")
            voz = audio.listen(source)
            comando = audio.recognize_google(voz, language='pt-BR')
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

def traduzir_clima(descricao):
    """Traduz a descrição do clima do inglês para o português."""
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

def executar_comando(comando):
    """Executa o comando de voz reconhecido."""
    global silencio
    if 'o que você pode fazer' in comando:
        Falar('Eu posso falar as horas e fazer pesquisas na Wikipédia.')
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
    elif 'youtube' in comando:
        Falar('Sim, senhor. Abrindo YouTube agora...')
        webbrowser.open('https://www.youtube.com')
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
        Falar("Você não me chamou pelo nome.")

def comando_voz_usuario():
    """Processa os comandos de voz do usuário."""
    while True:
        comando = reconhecer_comando()
        if comando and 'luna' in comando:
            comando = comando.replace('luna', '').strip()
            executar_comando(comando)
        else:
            Falar("Você não me chamou pelo nome.")

if __name__ == "__main__":
    comando_voz_usuario()
