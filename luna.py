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
import requests
import subprocess
import google.generativeai as genai
import pytz
import psutil
import shutil 
import tkinter as tk
from tkinter import scrolledtext
from dateutil import parser
from dotenv import load_dotenv
from PIL import Image, ImageTk
from collections import defaultdict
import speech_recognition as sr
from gtts import gTTS


audio = sr.Recognizer()
pygame.mixer.init()

load_dotenv()

senha_api = os.getenv('senha_api_tempo')
senha_api_news = os.getenv('senha_api_news')
senha_api_football = os.getenv('senha_api_football')
senha_api_gemini =os.getenv('senha_api_gemini')

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
def boasVindas():
    pygame.mixer.music.load('StartSound.mp3')
    pygame.mixer.music.play()
    Falar('Como posso ajudar?')

def Exbir(texto):
    resposta_area.insert(tk.END, texto + "\n")
    resposta_area.see(tk.END)

def Falar(texto):
    global silencio
    if silencio:
        return
    print("Luna: " + texto)
    Exbir("Luna: " + texto)
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
          
             # audio antes de ouvir
            audio_fala = "AI.mp3"
            pygame.mixer.music.load(audio_fala)

            pygame.mixer.music.play()
            Exbir("Estou ouvindo, fale algo")
            voz = audio.listen(source)
            comando = audio.recognize_google(voz, language='pt-BR')
            print("O usuário disse: " + comando)
            Exbir("O usuário disse: " + comando)
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

def Silencio(tempo=None):
    global silencio
    if tempo:
        silencio = True
        threading.Timer(tempo, desativar_silencio).start()
    else:
        silencio = True

def desativar_silencio():
    global silencio
    silencio = False
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

async def criar_pasta(nome_pasta):
    area_de_trabalho = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    caminho_pasta = os.path.join(area_de_trabalho, nome_pasta)

    try:
        os.makedirs(caminho_pasta, exist_ok=True)
        Falar(f"Pasta {nome_pasta} criada com sucesso na área de trabalho.")
    except Exception as e:
        Falar(f"Ocorreu um erro ao criar a pasta: {e}")

async def remover_pasta(nome_pasta):
    area_de_trabalho = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    caminho_pasta = os.path.join(area_de_trabalho, nome_pasta)

    try:

      if os.path.exists(caminho_pasta):
        Falar(f"Realmente deseja excluir a pasta ? {nome_pasta}")
        Falar('Diga sim se deseja excluir. ou não para cancelar')
        comando = Ouvir()
        if 'sim' in comando:
       
         Falar(f"Ok, excluindo pasta, {nome_pasta}")
         shutil.rmtree(caminho_pasta)
         Falar(f"Pasta {nome_pasta} exclluida com sucesso!")
     
        elif 'não' in comando:
         Falar(f"Ok, cancelando exclusão")
         return None
     
      else : Falar( f"Não foi loclizada a pasta {caminho_pasta}")

    except Exception as e:
        Falar(f"Ocorreu um erro ao tentar excluir a pasta: {e}")

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
   
    elif 'bom dia' in comando or 'boa tarde' in comando or 'boa noite' in comando:
        if hora >= 0 and hora < 12:
            Falar('Bom dia! Espero que você tenha um dia maravilhoso! Estou aqui sempre pronta para te ajudar.')
        elif hora >= 12 and hora < 18:
            Falar('boa tarde o que posso te ajudar?')
        else:
            Falar('boa noite o que faço por você?')

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
    
    elif 'notícias sobre' in comando:
       
        noticias = comando.replace('notícias de', '').strip()
        Falar('Procurando por notícias de ' + noticias)
        
        news = await news_api(noticias)  
      
        for artigo in news['articles'][:2]:  
         
            Falar(f"Título: {artigo['title']}")
           
            Falar(f"{artigo['description']}\n")
    
    elif 'jogos hoje' in comando:
       
       await obter_jogos_hoje()

    elif 'jogos ao vivo' in comando:
        Falar('obtendo jogos ao vivo')
        await obter_jogos_ao_vivo()

        if jogos_ao_vivo:

          Falar("Aqui estão os jogos ao vivo:")

          for jogo in jogos_ao_vivo:

                Falar(f"{jogo['home_team']} {jogo['score_home']} x {jogo['away_team']} {jogo['score_away']} - Status: {jogo['status']}")
        else:
            Falar("Não há jogos ao vivo no momento.")


    
    elif 'abra o' in comando:
        site = comando.replace('abra o', '').strip()
        await sites(site)
   
    elif 'toque ' in comando:
        comando = comando.replace('luna', '').strip()
        toque = comando.replace('toque', '').strip()
        Falar('Tocando ' + toque)
        threading.Thread(target=kit.playonyt, args=(toque,)).start()
        Silencio()

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

    elif 'desligue o microfone' in comando or 'fique em silêncio' in comando:
        silencio = True
        Falar("Ok, ficarei em silêncio.")
        Silencio()
    elif 'volte a falar' in comando or 'pode falar' in comando:
        silencio = False
        Falar("Ok, voltarei a falar.")
   
    elif 'criar pasta' in comando:
       
        Falar("Qual o nome da pasta?")
        
        nome_pasta = Ouvir()
      
        if nome_pasta:
         
          await  criar_pasta(nome_pasta)
       
        else:
            Falar("Não consegui entender o nome da pasta.")
    
    elif 'previsão do tempo em' in comando:
        cidade = comando.replace('previsão do tempo em', '').strip()
        Falar("Obtendo previsão do tempo em " + cidade)
        await obter_previsao(cidade)

    elif 'excluir pasta' in comando:
       
         Falar("Qual o nome da pasta que deseja excluir?")
       
         nome = Ouvir()

         await remover_pasta(nome)

    elif 'aumentar volume' in comando:
        Falar ('aumentar em quantos porcento?')
        porcentagem = int(Ouvir())
        aumentar_volume(porcentagem)
  
    elif 'diminuir volume' in comando:
        Falar ('diminuir em quantos porcento?')
        porcentagem = int(Ouvir())
        aumentar_volume(porcentagem)
    
    elif 'desligar computador' in comando:
        Falar('Seu computador será desligado em 30 segundos. Você pode cancelar o desligamento dizendo "cancelar desligamento".')
        os.system("shutdown /s /t 30")  # Comando para desligar em 30 segundos
    
    elif 'cancelar desligamento' in comando:
        os.system("shutdown /a")  # Comando para abortar o desligamento
        Falar("Desligamento cancelado.")
   
    elif 'reiniciar computador' in comando:
        Falar('Seu computador será reiniciado em 30 segundos. Você pode cancelar o reinício dizendo "cancelar reinício".')
     
        os.system("shutdown /r /t 30")  # Comando para reiniciar em 30 segundos
    
    elif 'cancelar reinício' in comando:
        os.system("shutdown /a")  # Comando para abortar o reinício
        Falar("Reinício cancelado.")
 
    elif 'nível de bateria' in comando:
        verificar_bateria()
    elif 'como você foi criada' in comando:
        Falar("Fui criada na linguagem python. para te ajudar em tarefas simples. meu criador foi um desenvolvedor chamado Felipe. se quiser entrar em contato acesse: https://github.com/felipesansi")
    elif 'comandos' in comando:
        apresentar_comandos()
 
    elif 'sair'    in comando or 'encerrar'in comando:
        Falar('até logo, encerrando assistente')
        exit()
        root.quit()  
        return
 
    else:
        Falar("Não sei vou falar com meu amigo gemini. ")
        await api_gemini(comando)

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

async def obter_previsao(cidade):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={senha_api}&units=metric"
        resposta = requests.get(url)
        resposta.raise_for_status()
        
        dados = resposta.json()
        
        previsoes_por_dia = defaultdict(list)
        for previsao in dados['list']:
            data = datetime.datetime.fromtimestamp(previsao['dt'])
            data_str = data.strftime('%Y-%m-%d')
            previsoes_por_dia[data_str].append(previsao)
        
        Falar(f"Previsão do tempo para {cidade} nos próximos 5 dias:")
        
        dias = list(previsoes_por_dia.keys())[:5]
        
        for dia in dias:
            previsao_dia = previsoes_por_dia[dia][0]
            data = datetime.datetime.fromtimestamp(previsao_dia['dt'])
            temperatura_min = previsao_dia['main']['temp_min']
            temperatura_max = previsao_dia['main']['temp_max']
            descricao = traduzir_clima(previsao_dia['weather'][0]['description'])
            Falar(f"Data: {data.strftime('%d/%m/%Y')}, Condição: {descricao}, Temperatura: entre {temperatura_min:.1f}°C e {temperatura_max:.1f}°C.")
        Falar(f"Essa foi a previsão do tempo obtida para cidade de {cidade}\n")    
    except requests.exceptions.HTTPError as e:
        Falar(f"Ocorreu um erro ao obter a previsão: {e}")
    except KeyError:
        Falar("Não consegui encontrar informações de previsão para a cidade especificada.")
    except Exception as e:
        Falar(f"Ocorreu um erro inesperado: {e}")
        
async def news_api(termo_pesquisa):
    url = f'https://newsapi.org/v2/everything?q={termo_pesquisa}&apiKey={senha_api_news}'
    resposta = requests.get(url)
    return resposta.json()  

async def api_gemini(texto_falado):
   
    texto = texto_falado.replace('luna', '').strip()
   
    try:
        genai.configure(api_key=senha_api_gemini)
        model = genai.GenerativeModel("gemini-pro")
   
        gemini_resposta = model.generate_content(texto)
        
        gemini_resposta_texto = gemini_resposta.text if hasattr(gemini_resposta, 'text') else str(gemini_resposta)
        repostaFormatada = gemini_resposta_texto.replace('*','')
        Falar(repostaFormatada)
        Falar("Deseja salvar a pergunta e a resposta nos comandos para ficar mais facíl ?")
        Falar("Se Sim diga: SIM. Caso contrário diga: NÃO")
        opcao = Ouvir()
       
        if 'sim' in opcao:
       
         Falar(f"Ok, Quando dizer: Luna, {texto} irei dizer a resposta anteriormente fornecida")
        
         await ensinar_luna(texto, repostaFormatada)
       
        elif 'não' in opcao:
       
         Falar("Ok, não irei salvar nada")
       
         return None

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def aumentar_volume(porcentagem):
    try:
        # Verifica se o nircmd.exe existe no diretório atual
        if os.path.exists('nircmd.exe'):
            # Define o volume máximo (em milissegundos)
            volume_maximo = 65535
            # Calcula o incremento do volume baseado na porcentagem
            incremento = int(volume_maximo * (porcentagem / 100))
            subprocess.run(['nircmd.exe', 'changesysvolume', str(incremento)])  # Aumenta o volume
            Falar(f"Volume aumentado em {porcentagem}%.")
        else:
            Falar("O comando para aumentar o volume não está disponível.")
    except Exception as e:
        Falar(f"Ocorreu um erro ao tentar aumentar o volume: {e}")

def diminuir_volume(porcentagem):
    try:
        if os.path.exists('nircmd.exe'):
            # Define o volume máximo (em milissegundos)
            volume_maximo = 65535
            # Calcula a redução do volume baseado na porcentagem
            decremento = int(volume_maximo * (porcentagem / 100))
            subprocess.run(['nircmd.exe', 'changesysvolume', str(-decremento)])  # Diminui o volume
            Falar(f"Volume diminuído em {porcentagem}%.")
        else:
            Falar("O comando para diminuir o volume não está disponível.")
    except Exception as e:
        Falar(f"Ocorreu um erro ao tentar diminuir o volume: {e}")

def verificar_bateria():
    bateria = psutil.sensors_battery() # informaçoes da bateria
    porcentagem =  bateria.percent
    carregando = bateria.power_plugged
    
    Falar(f"Nivel de bateria {porcentagem}%")
   
    if carregando:
        Falar("O computador está conectado no carregador")

def verificar_conexao_internet():
    url = "http://www.google.com"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("Conectado à internet.")
            return True
    except requests.ConnectionError:
        print("Sem conexão com a internet.")
        return False

def apresentar_comandos():
    comandos_disponiveis = [
        "adicionar comando: para adicionar um novo comando ao assistente.",
        "Comandos: lista as capacidades do assistente.",
        "bom dia, boa tarde, boa noite: cumprimentos baseados na hora.",
        "horas são: diz a hora atual.",
        "me diga sobre [tema]: fornece informações sobre um tema usando a Wikipédia.",
        "notícias de [tema]: busca por notícias relacionadas ao tema.",
        "abra o [site]: abre um site especificado (como google, instagram, etc.).",
        "toque [música]: toca uma música do YouTube.",
        "qual a temperatura em [cidade]: fornece a temperatura atual em uma cidade.",
        "procure por [termo]: faz uma pesquisa no Google.",
        "desligue o microfone: desliga a escuta do assistente.",
        "volte a falar: ativa novamente o assistente.",
        "criar pasta: cria uma nova pasta na área de trabalho.",
        "excluir pasta: exclui uma pasta especificada da área de trabalho.",
        "aumentar volume: aumenta o volume do sistema.",
        "Jogos ao vivo: listas os jogos ao vivo das partidas de futebol do mundo",
        "Jogos de hoje: lista os jogos das competições de hoje",
        "diminuir volume: diminui o volume do sistema.",
        "desligar computador: desliga o computador após 30 segundos.",
        "reiniciar computador: reinicia o computador após 30 segundos.",
        "como você foi criada : explicação de como fui criada!",
        "nível de bateria: informa o nível da bateria do computador.",
        "sair: encerra o assistente."
    ]

    # Exibe os comandos na área de resposta
    Exbir("Comandos disponíveis:")
    for comando in comandos_disponiveis:
        Exbir(comando)
        Falar(comando)

def iniciar_assistente():
    boasVindas()
    while True:
        comando = Ouvir()
        if comando is not None and 'luna' in comando:
            desativar_silencio()
            asyncio.run(executar_comando(comando))
        else:
            Falar("você não me chamou pelo nome")

def iniciar_thread_assistente():
    threading.Thread(target=iniciar_assistente).start()

# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Assistente Virtual Luna")

# Mudar cor de fundo da janela
root.config(bg="black")# Substitua "lightblue" pela cor desejada
root.geometry("400x400")  # 

janela = tk.Frame(root)
janela.pack(pady=10)


# Carregar o GIF animado
gif_path = "Luna.gif"  # Substitua pelo caminho do seu GIF
gif_image = Image.open(gif_path)

# Criar um label para exibir o GIF
label_gif = tk.Label(root)
label_gif.pack()

# Função para atualizar o GIF
def atualizar_gif():
    try:
        gif_image.seek(label_gif.index)  # Move para o próximo frame do GIF
        photo = ImageTk.PhotoImage(gif_image)
        label_gif.config(image=photo)
        label_gif.image = photo  # Manter referência da imagem
        label_gif.index += 1
    except EOFError:
        label_gif.index = 0  # Reinicia o GIF
    label_gif.after(100, atualizar_gif)  # Atualiza a cada 100ms

label_gif.index = 0  # Inicializa o índice do GIF
atualizar_gif()  # Inicia a atualização do GIF



# Adicionando a área de resposta
resposta_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=2, bg="black", fg="white")  # Ajuste a cor de fundo da área de texto
resposta_area.pack(pady=10)


# Iniciar a thread do assistente
iniciar_thread_assistente()

root.mainloop()
