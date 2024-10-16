# Luna - Assistente Virtual

Luna é uma assistente virtual construída em Python, capaz de realizar diversas tarefas através de comandos de voz. Ela pode responder perguntas, tocar músicas, fornecer informações sobre o clima, e muito mais!

## Funcionalidades

- **Reconhecimento de Voz**: Ouça e reconheça comandos falados.
- **Respostas por Voz**: Responda ao usuário com síntese de voz.
- **Informações Climáticas**: Consulte a temperatura e condições meteorológicas de qualquer cidade.
- **Pesquisas na Web**: Realize buscas no Google e Wikipedia.
- **Abertura de Sites**: Abra sites populares como Google, Instagram, Facebook, Spotify e GitHub.
- **Toque de Músicas**: Reproduza músicas diretamente do YouTube.
- **Notícias**: Consulte as últimas notícias de vários tópicos.
- **Comandos Personalizados**: Aprenda novos comandos que o usuário ensina.

## Pré-requisitos

- Python 3.6 ou superior
- Bibliotecas necessárias:
  - `speech_recognition`
  - `gtts`
  - `pygame`
  - `wikipedia`
  - `pywhatkit`
  - `pyowm`
  - `requests`
  - `python-dotenv`

Você pode instalar as bibliotecas necessárias com o seguinte comando:

```bash
pip install speech_recognition gtts pygame wikipedia-api pywhatkit pyowm requests python-dotenv
```

## Configuração

1. **Obtenha suas chaves de API**:

   - Crie uma conta em [OpenWeatherMap](https://openweathermap.org/) para obter a chave da API do clima.
   - Crie uma conta em [NewsAPI](https://newsapi.org/) para obter a chave da API de notícias.
```bash
senha_api_tempo=SEU_API_KEY_DO_CLIMA
senha_api_news=SEU_API_KEY_DE_NOTÍCIAS
```

