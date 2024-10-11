# # Assistente Virtual em Python

Este projeto é um assistente virtual desenvolvido em Python que utiliza reconhecimento de voz e síntese de fala. O assistente pode responder a perguntas, fornecer informações sobre o clima, tocar músicas e executar pesquisas na Wikipédia e no Google.

## Funcionalidades

- **Reconhecimento de voz**: Escuta comandos dados pelo usuário.
- **Síntese de fala**: Responde ao usuário com uma voz gerada por texto.
- **Informações do clima**: Obtém a temperatura e a descrição do clima em uma cidade específica.
- **Pesquisas na Wikipédia**: Realiza buscas e fornece resumos de artigos da Wikipédia.
- **Abertura de sites**: Abre URLs específicas, como o YouTube.
- **Toque de músicas**: Toca músicas do YouTube com base no comando do usuário.
- **Modo silencioso**: Permite ao usuário silenciar o assistente temporariamente.

## Pré-requisitos

Antes de executar o assistente, verifique se você tem as seguintes bibliotecas instaladas:

- `speech_recognition`
- `gtts`
- `pygame`
- `wikipedia`
- `pywhatkit`
- `pyowm`

Você pode instalá-las utilizando o seguinte comando:

```bash
pip install speech_recognition gtts pygame wikipedia pywhatkit pyowm
