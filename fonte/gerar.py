from pathlib import Path
from PIL import Image

PALETA = {
    ".": (0, 21, 42),
    "d": (128, 92, 46),
    "g": (198, 158, 84),
    "l": (234, 204, 130),
    "w": (252, 240, 200),
}
RAIZ = Path(__file__).resolve().parent.parent


def ler_grade(arquivo):
    linhas = [l for l in arquivo.read_text(encoding="utf-8").splitlines() if l.strip()]
    largura = max(len(l) for l in linhas)
    return [l.ljust(largura, ".") for l in linhas]


def desenhar(grade, transparente=False):
    modo = "RGBA" if transparente else "RGB"
    imagem = Image.new(modo, (len(grade[0]), len(grade)))
    for y, linha in enumerate(grade):
        for x, letra in enumerate(linha):
            cor = PALETA[letra]
            if transparente:
                cor = (0, 0, 0, 0) if letra == "." else cor + (255,)
            imagem.putpixel((x, y), cor)
    return imagem


def salvar_ampliado(imagem, destino, escala):
    largura, altura = imagem.size
    imagem.resize((largura * escala, altura * escala), Image.NEAREST).save(destino)


grade = ler_grade(RAIZ / "fonte" / "simbolo.txt")
pasta = RAIZ / "simbolo"
pasta.mkdir(exist_ok=True)
for transparente, sufixo in ((False, ""), (True, "-transparente")):
    simbolo = desenhar(grade, transparente)
    simbolo.save(pasta / f"simbolo-32{sufixo}.png")
    for escala in (8, 16, 32):
        salvar_ampliado(simbolo, pasta / f"simbolo-{32 * escala}{sufixo}.png", escala)
