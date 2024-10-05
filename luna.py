import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia

# Inicializa o reconhecedor
audio = sr.Recognizer()
maquina = pyttsx3.init()

def executa_comando():
    try:
        with sr.Microphone() as source:
            print("Ouvindo... Diga algo:")
            audio.adjust_for_ambient_noise(source)  # Ajusta para o ruído ambiente
            voz = audio.listen(source)
            comando = audio.recognize_google(voz, language='pt-BR')
            return comando.lower()  # Retorna o comando em minúsculas
    except sr.UnknownValueError:
        print("Não consegui entender o áudio.")
        return None
    except sr.RequestError:
        print("Erro ao se conectar ao serviço de reconhecimento de voz.")
        return None
    except Exception as e:
        print("Ocorreu um erro:", e)
        return None

def comando_voz_usuario():
    while True:
        comando = executa_comando()
        if comando:
            if 'luna' in comando:  
                comando = comando.replace('luna', '').strip()
                
                if 'o que você pode fazer' in comando:
                    maquina.say('Eu posso falar as horas e fazer pesquisas na Wikipédia.')
                    maquina.runAndWait()
                
                elif 'horas são' in comando:
                    horas = datetime.datetime.now().strftime('%H:%M')
                    maquina.say("Agora são " + horas)
                    maquina.runAndWait()
                
                elif 'me diga sobre' in comando or 'me fale sobre' in comando:
                    if 'me diga sobre' in comando:
                        sobre = comando.replace('me diga sobre', '').strip()
                    else:
                        sobre = comando.replace('me fale sobre', '').strip()

                    wikipedia.set_lang('pt')
                    try:
                        resposta = wikipedia.summary(sobre, 2)
                        maquina.say(resposta)
                        maquina.runAndWait()
                    
                    except wikipedia.exceptions.DisambiguationError:
                        maquina.say("A pesquisa retornou múltiplas opções. Por favor, seja mais específico.")
                        maquina.runAndWait()

            else:
                maquina.say("Você não chamou pelo nome Luna.")
                maquina.runAndWait()

comando_voz_usuario()
