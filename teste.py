import speech_recognition as sr
from gtts import gTTS
import datetime
import wikipedia
import os
import pygame
import time
import webbrowser
import pywhatkit as kit
import threading

# Inicializa o reconhecedor de voz e o mixer do pygame
audio = sr.Recognizer()
pygame.mixer.init()

# Variável global para controle da fala
interromper_fala = threading.Event()

def Falar(texto):
    """Converte texto em fala usando gTTS e reproduz o áudio gerado."""
    global interromper_fala
    print(texto)  # Para visualizar o que está sendo dito
    arquivo_audio = f"resposta_{int(time.time())}.mp3"  # Nome único baseado no timestamp

    tts = gTTS(text=texto, lang='pt-br')
    tts.save(arquivo_audio)
    
    pygame.mixer.music.load(arquivo_audio)
    pygame.mixer.music.play()
    
    # Aguardar até a reprodução terminar
    while pygame.mixer.music.get_busy():
        if interromper_fala.is_set():
            pygame.mixer.music.stop()
            break
        time.sleep(0.1)

    # Remove o arquivo após a reprodução
  #  os.remove(arquivo_audio)

def executa_comando():
    """Reconhece o comando de voz do usuário."""
    try:
        with sr.Microphone() as source:
            Falar("Estou ouvindo")
            audio.adjust_for_ambient_noise(source)  # Ajusta para o ruído ambiente
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

def monitorar_comandos():
    global interromper_fala
    while True:
        comando = executa_comando()
        if comando:
            if 'luna' in comando:
                comando = comando.replace('luna', '').strip()
                
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
                    webbrowser.open('youtube.com')
                    
                elif 'toque' in comando:
                    toque = comando.replace('toque', '').strip()
                    Falar('Tocando ' + toque)
                    kit.playonyt(toque)
                
                elif 'procure por' in comando:
                    pesquisa = comando.replace('procure por', '').strip()
                    Falar('Procurando no Google por ' + pesquisa)
                    kit.search(pesquisa)
                
                elif 'sair' in comando or 'encerrar' in comando:
                    Falar("Encerrando o assistente. Até logo!")
                    break  

                elif 'pare de falar' in comando or 'pare' in comando:
                    interromper_fala.set()
                    Falar('Parando de falar.')
                    interromper_fala.clear()

            else:
                Falar("Você não chamou pelo nome Luna.")

def comando_voz_usuario():
    """Inicia a thread para monitorar comandos e mantém o programa rodando."""
    thread_comandos = threading.Thread(target=monitorar_comandos)
    thread_comandos.daemon = True
    thread_comandos.start()

    # Loop principal que mantém o programa rodando
    while True:
        time.sleep(1)

if __name__ == "__main__":
    comando_voz_usuario()
