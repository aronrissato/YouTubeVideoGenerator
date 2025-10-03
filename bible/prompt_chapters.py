import google.generativeai as genai
import datetime
from file_chapters import get_chapter
from dotenv import load_dotenv


def get_speech(api_key, select_model):
    chapter = get_chapter()

    speech_prompt = f"""Estou usando o seu retorno como prompt para um programa, então respeite as regras abaixo:
    Conte todos os versículos, em ingles, do capítulo da biblia que será dito no final desse texto.
     Somente o texto, como um bloco de texto, sem cabeçalho ou marcaçoes de inicio e fim do versículo.
     Coloque todos juntos como se fosse um unico bloco de texto, sem a numeração no começo do versículo.
     No início do texto, adicione primeiro o nome do capítulo e em seguida dois pontos, com o texto acima gerado.
     Capítulo: {chapter}"""

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(select_model)

    prompt = speech_prompt
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        if "API key not valid" in str(e):
            print("Error: Invalid Gemini API key. Please check your Gemini API key in .env file")
        return {"text": "Error generating text", "chapter": "Error"}

    print("- - -   RESULTADO GERADO   - - -")
    print(text)

    return {"text": text, "chapter": chapter}


if __name__ == "__main__":
    import os

    load_dotenv()
    api_key = os.getenv("KEY_GEMINI")
    select_model = "gemini-1.5-flash"
    get_speech(api_key, select_model)
