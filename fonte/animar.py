import json
import math

from PIL import Image

from gerar import FONTE, RAIZ, avatar, desenhar, ler_grade, ler_letras, logo_vertical

QUADROS = 32
DURACAO_MS = 90
CENTRO_CRISTAL = 33
ESTRELAS = [(50, 8, 4, 0.0), (8, 30, 3, 0.35), (54, 30, 1, 0.7)]
PONTOS = [(47, 18, 0.15), (42, 25, 0.55), (13, 10, 0.8), (57, 50, 0.3), (20, 59, 0.65), (5, 57, 0.95)]


def mais_claro(tom, passos):
    return str(max(1, min(6, int(tom) + passos)))


def dentro_do_cristal(x, y):
    topo, ombro, quadril, base, meia = 33, 38, 49, 59, 6.5
    py = y + 0.5
    if py < topo or py > base:
        return False
    if py < ombro:
        largura = meia * (py - topo) / (ombro - topo)
    elif py <= quadril:
        largura = meia
    else:
        largura = meia * (base - py) / (base - quadril)
    return abs(x + 0.5 - CENTRO_CRISTAL) <= largura


def pontos_da_orbita(base):
    caminho = []
    for k in range(720):
        angulo = 2 * math.pi * k / 720
        ex, ey = 27 * math.cos(angulo), 5.2 * math.sin(angulo)
        giro = math.radians(-8)
        x = int(CENTRO_CRISTAL + ex * math.cos(giro) - ey * math.sin(giro))
        y = int(46 + ex * math.sin(giro) + ey * math.cos(giro))
        visivel = base[y][x] != "." and not dentro_do_cristal(x, y)
        if visivel and (not caminho or caminho[-1] != (x, y)):
            caminho.append((x, y))
    return caminho


def piscar(grade, x, y, braco, brilho):
    alcance = round(braco * (0.5 + 0.5 * brilho))
    for dx in range(-braco - 1, braco + 2):
        for dy in range(-braco - 1, braco + 2):
            px, py = x + dx, y + dy
            if grade[py][px] == ".":
                continue
            distancia = max(abs(dx), abs(dy))
            diagonal = dx != 0 and dy != 0
            if diagonal and alcance < braco:
                grade[py][px] = "."
                continue
            if distancia > alcance and not (braco == 1 and distancia == 1 and brilho > -0.3):
                grade[py][px] = "."
    if brilho > 0.6:
        grade[y][x] = "6"


def quadro_do_simbolo(base, orbita, n):
    grade = [list(linha) for linha in base]
    fase = n / QUADROS
    for x, y, braco, atraso in ESTRELAS:
        piscar(grade, x, y, braco, math.cos(2 * math.pi * (fase - atraso)))
    for x, y, atraso in PONTOS:
        if math.cos(2 * math.pi * (fase - atraso)) < -0.3:
            grade[y][x] = "2"
    faixa = -12 + fase * 64
    for y in range(64):
        for x in range(64):
            if dentro_do_cristal(x, y) and abs((x - CENTRO_CRISTAL) * 0.6 + y - 33 - faixa) < 1.6:
                grade[y][x] = mais_claro(grade[y][x], 2)
    for rastro in range(3):
        x, y = orbita[(int(fase * len(orbita)) - rastro * 2) % len(orbita)]
        grade[y][x] = "6" if rastro == 0 else "5"
    return ["".join(linha) for linha in grade]


def ampliar(grade, escala):
    imagem = desenhar(grade)
    return imagem.resize((imagem.width * escala, imagem.height * escala), Image.NEAREST)


def salvar_animacao(quadros, pasta, nome, escala):
    imagens = [ampliar(q, escala) for q in quadros]
    imagens[0].save(
        pasta / f"{nome}-{escala}x.gif",
        save_all=True,
        append_images=imagens[1:],
        duration=DURACAO_MS,
        loop=0,
        disposal=1,
        optimize=False,
    )
    folha = Image.new("RGB", (imagens[0].width * len(imagens), imagens[0].height))
    for i, imagem in enumerate(imagens):
        folha.paste(imagem, (i * imagem.width, 0))
    folha.save(pasta / f"{nome}-{escala}x-folha.png")


def gerar_animacoes():
    base = ler_grade(FONTE / "simbolo.txt")
    letras = ler_letras(FONTE / "letras.txt")
    orbita = pontos_da_orbita(base)
    simbolos = [quadro_do_simbolo(base, orbita, n) for n in range(QUADROS)]
    pasta = RAIZ / "animacao"
    pasta.mkdir(exist_ok=True)
    for antigo in pasta.glob("*"):
        antigo.unlink()
    salvar_animacao([avatar(s, 8) for s in simbolos], pasta, "avatar", 8)
    salvar_animacao([logo_vertical(s, letras) for s in simbolos], pasta, "logo-vertical", 4)
    salvar_animacao(simbolos, pasta, "simbolo", 4)
    tempo = {"quadros": QUADROS, "duracao_ms": DURACAO_MS, "laco": True}
    (pasta / "tempo.json").write_text(json.dumps(tempo, indent=2) + "\n", encoding="utf-8")




if __name__ == "__main__":
    gerar_animacoes()
