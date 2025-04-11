import os
import json
from datetime import datetime
import re
import time
import unicodedata
import uuid
from dotenv import load_dotenv
from gtts import gTTS
from openai import OpenAI
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

os.makedirs("podcastRot", exist_ok=True)
os.makedirs("Podcasts", exist_ok=True)
os.makedirs("logs", exist_ok=True)
open("logs/errors.log", "a", encoding="utf-8").close()

def sanitize_filename(name):
    nfkd = unicodedata.normalize('NFKD', name)
    name_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^a-zA-Z0-9_]', '', name_ascii).replace(" ", "_").lower()
def log_error(podcast_id, error_message, step):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "podcast_id": podcast_id,
        "step": step,
        "error_message": error_message
    }
    with open("logs/errors.log", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

num_pod = 10
for i in range(0, num_pod):
    podcast_id = str(uuid.uuid4())

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Gerando conteúdo para o podcast {podcast_id}")

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                "role": "system",
                "content": (
                    "Você é um roteirista especializado na criação de podcasts. Crie roteiros completos e envolventes com um mínimo de 1000 palavras, escritos de forma natural e fluida, como se fossem lidos diretamente por um narrador durante a gravação. "
                    "O conteúdo deve ser contínuo, sem interrupções por seções extras como 'perguntas frequentes', 'recursos adicionais', ou 'informações de contato'. "
                    "Não use formatações como negrito (**), itálico (*), ou marcadores de tópico. "
                    "Não adicione títulos, divisões em partes, ou blocos como Parte 1, Parte 2, Conclusão, etc. "
                    "Não utilize marcações como [música] ou quaisquer colchetes. "
                    "Apenas escreva o texto que será falado, como se estivesse saindo da boca do apresentador em tempo real. "
                    "Evite linguagem robótica e mantenha um tom acessível, informal e empático, como se estivesse conversando diretamente com o ouvinte. "
                    "O conteúdo deve durar aproximadamente 7 minutos de fala contínua."
                )
                },
                                {
                "role": "user",
                "content": (
                    f"Crie um roteiro de podcast com no mínimo 1000 palavras sobre qualquer tema de sua escolha. "
                    "O texto deve ser envolvente, em tom de conversa direta com o ouvinte, como se estivesse sendo narrado em um podcast real. "
                    "Não use linguagem técnica demais. Mantenha a fluidez e naturalidade ao longo de todo o conteúdo. "
                    "Evite qualquer marcação de áudio como [música], [efeitos], etc. Produza o texto como se fosse lido do início ao fim por um narrador."
                )
}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        print("roteiro criado com sucesso")
    except Exception as e:
        print(f"Erro ao gerar roteiro: {e}")
        log_error(podcast_id=podcast_id, error_message=e, step="geração de roteiro")
        continue

    podcast_text = response.choices[0].message.content.strip()


    try:
        script_file_name = os.path.join("podcastRot", f"{podcast_id}.txt")
        with open(script_file_name, 'w') as a:
            a.write(podcast_text)
        print("roteiro salvo com sucesso")
    except Exception as e:
        print(f"Erro ao salvar roteiro do podcast: {e}")
        log_error(podcast_id=podcast_id, error_message=e, step="salvar roteiro")
        continue
        


    print(f"Convertendo texto em voz...")
    try:
        voice = gTTS(text=podcast_text, lang='pt-br')
        voice_file_name = os.path.join("Podcasts", f"{podcast_id}.mp3")
        voice.save(voice_file_name)
    except Exception as e:
        print(f"erro ao gerar voz do podcast: {e}")
        log_error(podcast_id=podcast_id, error_message=e, step="gerar voz")
        continue

    print(f"Podcast {podcast_id} salvo com sucesso como '{voice_file_name}'\n")
    time.sleep(2)