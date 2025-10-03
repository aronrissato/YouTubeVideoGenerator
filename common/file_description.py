import google.generativeai as genai
import datetime


def get_description(api_key, select_model, prompt_gemini):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(select_model)

    prompt = prompt_gemini
    response = model.generate_content(prompt)
    text = response.text.strip()

    print("- - -   RESULTADO GERADO   - - -")
    print(text)

    return text


if __name__ == "__main__":
    api_key = ""
    select_model = "gemini-1.5-flash"
    prompt_gemini = "Gere um título e uma descrição inspirado no dia da semana de hoje, em ingles para um vídeo do YouTube. Estou te usando como prompt então envie exatamente no formato que eu te pedir, somente uma opção."

    resposta = gen_description(api_key, select_model, prompt_gemini)
    print(f"Geração teste:\n {resposta}")
