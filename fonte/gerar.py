from pathlib import Path
from PIL import Image


def cor_15_bits(cor):
    return tuple((canal // 8) * 8 for canal in cor)


OURO = [(78, 44, 34), (124, 78, 44), (172, 118, 58), (208, 160, 82), (236, 202, 126), (252, 238, 192)]
PALETA = {".": cor_15_bits((0, 21, 42))}
PALETA.update({str(i + 1): cor_15_bits(cor) for i, cor in enumerate(OURO)})
FONTE = Path(__file__).resolve().parent
RAIZ = FONTE.parent
ESPACO_LETRAS = {"grande": 2, "pequena": 4}


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


def scale2x(mascara):
    altura, largura = len(mascara), len(mascara[0])

    def ponto(x, y):
        if 0 <= x < largura and 0 <= y < altura:
            return mascara[y][x]
        return False

    saida = [[False] * (largura * 2) for _ in range(altura * 2)]
    for y in range(altura):
        for x in range(largura):
            centro = ponto(x, y)
            cima, baixo, esquerda, direita = ponto(x, y - 1), ponto(x, y + 1), ponto(x - 1, y), ponto(x + 1, y)
            e0 = e1 = e2 = e3 = centro
            if cima != baixo and esquerda != direita:
                e0 = esquerda if cima == esquerda else centro
                e1 = direita if cima == direita else centro
                e2 = esquerda if baixo == esquerda else centro
                e3 = direita if baixo == direita else centro
            saida[y * 2][x * 2], saida[y * 2][x * 2 + 1] = e0, e1
            saida[y * 2 + 1][x * 2], saida[y * 2 + 1][x * 2 + 1] = e2, e3
    return saida


def sombrear_letra(mascara):
    altura, largura = len(mascara), len(mascara[0])

    def cheio(x, y):
        return 0 <= x < largura and 0 <= y < altura and mascara[y][x]

    faixas = "665544433"
    grade = [["."] * largura for _ in range(altura)]
    for y in range(altura):
        for x in range(largura):
            if not mascara[y][x]:
                continue
            tom = faixas[min(len(faixas) - 1, y * len(faixas) // altura)]
            borda_de_baixo = not cheio(x, y + 1)
            borda_da_direita = not cheio(x + 1, y)
            borda_de_cima = not cheio(x, y - 1)
            if borda_de_baixo:
                tom = "2"
            elif borda_da_direita:
                tom = str(max(2, int(tom) - 1))
            elif borda_de_cima and y < altura // 2:
                tom = "6"
            grade[y][x] = tom
    return grade


def palavra(letras, tamanho, texto):
    glifos = [scale2x([[p == "#" for p in linha] for linha in letras[(tamanho, letra)]]) for letra in texto]
    espaco = ESPACO_LETRAS[tamanho]
    largura = sum(len(g[0]) for g in glifos) + espaco * (len(glifos) - 1)
    mascara = [[False] * largura for _ in range(len(glifos[0]))]
    x0 = 0
    for glifo in glifos:
        for y, linha in enumerate(glifo):
            for x, cheio in enumerate(linha):
                mascara[y][x0 + x] = mascara[y][x0 + x] or cheio
        x0 += len(glifo[0]) + espaco
    return ["".join(l) for l in sombrear_letra(mascara)]


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


def letreiro(letras):
    return (
        palavra(letras, "grande", "MAGIN"),
        palavra(letras, "grande", "DREAMERS"),
        palavra(letras, "pequena", "STUDIO"),
    )


def logo_vertical(simbolo, letras):
    magin, dreamers, studio = letreiro(letras)
    largura = len(dreamers[0]) + 16
    return empilhar_centralizado([(simbolo, 4), (magin, 6), (dreamers, 8), (studio, 0)], largura, 8)


def logo_horizontal(simbolo, letras):
    magin, dreamers, studio = letreiro(letras)
    texto = empilhar_centralizado([(magin, 6), (dreamers, 8), (studio, 0)], len(dreamers[0]), 0)
    margem = 8
    largura = margem * 2 + len(simbolo[0]) + 4 + len(texto[0])
    altura = margem * 2 + max(len(simbolo), len(texto))
    grade = tela(largura, altura)
    colar(grade, simbolo, margem, (altura - len(simbolo)) // 2)
    colar(grade, texto, margem + len(simbolo[0]) + 4, (altura - len(texto)) // 2)
    return grade


def avatar(simbolo, margem):
    grade = tela(len(simbolo[0]) + margem * 2, len(simbolo) + margem * 2)
    colar(grade, simbolo, margem, margem)
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
for pasta in ("simbolo", "logo", "avatar"):
    for antigo in (RAIZ / pasta).glob("*.png"):
        antigo.unlink()
salvar(simbolo, RAIZ / "simbolo", "simbolo", (4, 8, 16))
salvar(logo_vertical(simbolo, letras), RAIZ / "logo", "logo-vertical", (2, 4, 8))
salvar(logo_horizontal(simbolo, letras), RAIZ / "logo", "logo-horizontal", (2, 4, 8))
salvar(avatar(simbolo, 8), RAIZ / "avatar", "avatar", (8, 16))
