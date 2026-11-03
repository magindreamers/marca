from pathlib import Path
from PIL import Image

PALETA = {
    ".": (0, 21, 42),
    "d": (128, 92, 46),
    "g": (198, 158, 84),
    "l": (234, 204, 130),
    "w": (252, 240, 200),
}
FONTE = Path(__file__).resolve().parent
RAIZ = FONTE.parent
ESPACO_LETRAS = {"grande": 1, "pequena": 2}


def ler_grade(arquivo):
    linhas = [l for l in arquivo.read_text(encoding="utf-8").splitlines() if l.strip()]
    largura = max(len(l) for l in linhas)
    return [l.ljust(largura, ".") for l in linhas]


def ler_letras(arquivo):
    letras = {}
    atual = None
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        if linha.startswith("# ") or not linha.strip():
            continue
        if linha.startswith("== "):
            tamanho, letra = linha[3:].split()
            atual = letras.setdefault((tamanho, letra), [])
        else:
            atual.append(linha)
    return letras


def cor_da_linha(tamanho, y):
    if tamanho == "pequena":
        return "g"
    return "l" if y < 4 else "g"


def palavra(letras, tamanho, texto):
    glifos = [letras[(tamanho, letra)] for letra in texto]
    espaco = ESPACO_LETRAS[tamanho]
    largura = sum(len(g[0]) for g in glifos) + espaco * (len(glifos) - 1)
    altura = len(glifos[0])
    grade = [["."] * largura for _ in range(altura)]
    x0 = 0
    for glifo in glifos:
        for y, linha in enumerate(glifo):
            for x, ponto in enumerate(linha):
                if ponto == "#":
                    grade[y][x0 + x] = cor_da_linha(tamanho, y)
        x0 += len(glifo[0]) + espaco
    return ["".join(l) for l in grade]


def colar(destino, grade, x0, y0):
    for y, linha in enumerate(grade):
        for x, letra in enumerate(linha):
            if letra != ".":
                destino[y0 + y][x0 + x] = letra


def tela(largura, altura):
    return [["."] * largura for _ in range(altura)]


def empilhar_centralizado(blocos, largura, margem):
    altura = margem * 2 + sum(len(b) for b, _ in blocos) + sum(espaco for _, espaco in blocos[:-1])
    grade = tela(largura, altura)
    y = margem
    for bloco, espaco in blocos:
        colar(grade, bloco, (largura - len(bloco[0])) // 2, y)
        y += len(bloco) + espaco
    return grade


def logo_vertical(simbolo, letras):
    magin = palavra(letras, "grande", "MAGIN")
    dreamers = palavra(letras, "grande", "DREAMERS")
    studio = palavra(letras, "pequena", "STUDIO")
    largura = len(dreamers[0]) + 8
    return empilhar_centralizado([(simbolo, 2), (magin, 3), (dreamers, 4), (studio, 0)], largura, 4)


def logo_horizontal(simbolo, letras):
    magin = palavra(letras, "grande", "MAGIN")
    dreamers = palavra(letras, "grande", "DREAMERS")
    studio = palavra(letras, "pequena", "STUDIO")
    texto = empilhar_centralizado([(magin, 3), (dreamers, 4), (studio, 0)], len(dreamers[0]), 0)
    margem = 4
    largura = margem * 2 + len(simbolo[0]) + 2 + len(texto[0])
    altura = margem * 2 + max(len(simbolo), len(texto))
    grade = tela(largura, altura)
    colar(grade, simbolo, margem, (altura - len(simbolo)) // 2)
    colar(grade, texto, margem + len(simbolo[0]) + 2, (altura - len(texto)) // 2)
    return grade


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


def salvar(grade, pasta, nome, escalas):
    pasta.mkdir(exist_ok=True)
    for transparente, sufixo in ((False, ""), (True, "-transparente")):
        imagem = desenhar(grade, transparente)
        imagem.save(pasta / f"{nome}-1x{sufixo}.png")
        largura, altura = imagem.size
        for escala in escalas:
            ampliada = imagem.resize((largura * escala, altura * escala), Image.NEAREST)
            ampliada.save(pasta / f"{nome}-{escala}x{sufixo}.png")


simbolo = ler_grade(FONTE / "simbolo.txt")
letras = ler_letras(FONTE / "letras.txt")
salvar(simbolo, RAIZ / "simbolo", "simbolo", (8, 16, 32))
salvar(logo_vertical(simbolo, letras), RAIZ / "logo", "logo-vertical", (4, 8, 16))
salvar(logo_horizontal(simbolo, letras), RAIZ / "logo", "logo-horizontal", (4, 8, 16))
