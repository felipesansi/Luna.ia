# Assistente Virtual Luna

Luna é um assistente virtual desenvolvido em Python, capaz de reconhecer comandos de voz e realizar diversas funções, como fornecer informações sobre o clima, tocar músicas, buscar notícias e muito mais. Este projeto utiliza várias bibliotecas para funcionalidades avançadas.

## Funcionalidades

- **Reconhecimento de voz:** Capaz de entender comandos falados pelo usuário.
- **Leitura de texto:** Converte texto em fala utilizando o Google Text-to-Speech (gTTS).
- **Informações do clima:** Consulta previsões do tempo utilizando a API OpenWeatherMap.
- **Busca de notícias:** Obtém as últimas notícias de diferentes fontes usando a News API.
- **Jogatinas ao vivo:** Informa sobre jogos de futebol em andamento utilizando a API Football.
- **Gerenciamento de arquivos:** Permite criar e excluir pastas no sistema.
- **Controle de volume:** Aumenta ou diminui o volume do sistema.
- **Integração com o Gemini:** Conecta-se ao modelo de geração de texto do Google Gemini.

## Instalação

### Pré-requisitos

Certifique-se de ter Python 3.x instalado em sua máquina. Você pode baixar a versão mais recente do Python [aqui](https://www.python.org/downloads/).

### Dependências

Instale as dependências necessárias com o seguinte comando:

```bash
pip install SpeechRecognition gtts pygame wikipedia-api pyowm pywhatkit requests python-dotenv google-generativeai Pillow psutil python-dateutil
```

## .Env

Para ter acesso aos comando de **Futebol** , **Previsão do tempo**, **Noticías**  e **Gemini**. <br>  

Você precisa obter a **API KEY** nas segintes plataformas: <br>
### Sites
[api-football.com](http://www.api-football.com) <br> 
[openweathermap.org](https://www.openweathermap.org) <br> 
[gemini-api.com](https://ai.google.dev/gemini-api/docs) <br> 
[news.org](https://newsapi.org)

Após criar todas as **API KEY**  e anota-las crie um arquivo chamado *.env* e crie **4** variáveis com os nomes: <br><br>
  
  ### Exemplo de KEY
 
 *senha_api_tempo* = 555856959569 <br> 
 *senha_api_news* =  555856959569 <br>
 *senha_api_football* = 555856959569 <br>
 *senha_api_gemini* = 555856959569

## Conclusão
Este projeto foi desenvolvido como um exercício de programação em Python. Espero que você tenha gostdo  e consiga explorar suas funcionalidades e que ele inspire futuros projetos e aprendizados.

