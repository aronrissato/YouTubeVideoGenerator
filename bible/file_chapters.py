import random
import os


def get_chapter(arquivo="chapters.txt"):
    caminho_absoluto = os.path.join(os.path.dirname(__file__), arquivo)
    with open(caminho_absoluto, "r", encoding="utf-8") as f:
        capitulos = [linha.strip() for linha in f if linha.strip()]
    return random.choice(capitulos)


if __name__ == "__main__":
    capitulo = get_chapter()
    print(capitulo)
