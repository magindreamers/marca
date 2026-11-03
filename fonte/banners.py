import math
import random

from PIL import Image

from gerar import FONTE, RAIZ, cor_15_bits, desenhar, ler_grade, ler_letras, logo_horizontal

NOITE = [cor_15_bits(c) for c in [(0, 8, 24), (0, 16, 40), (8, 30, 62), (22, 44, 84), (38, 60, 106), (60, 82, 130)]]
OURO = [cor_15_bits(c) for c in [(78, 44, 34), (124, 78, 44), (172, 118, 58), (208, 160, 82), (236, 202, 126), (252, 238, 192)]]

BANNERS = {
    "trello-1920x1080": ((1920, 1080), 3, "direita"),
    "youtube-2560x1440": ((2560, 1440), 4, "centro"),
    "x-1500x500": ((1500, 500), 3, "centro"),
    "linkedin-1128x191": ((1128, 191), 2, "centro"),
    "discord-960x540": ((960, 540), 2, "centro"),
}


def ceu(largura, altura, sorteio):
    imagem = Image.new("RGB", (largura, altura))
    degraus = len(NOITE) * 2 - 1
    for y in range(altura):
        posicao = (y / altura) ** 1.3 * (len(NOITE) - 1)
        for x in range(largura):
            tom = int(posicao)
            meio = posicao - tom > 0.5 and (x + y) % 2 == 0
            imagem.putpixel((x, y), NOITE[min(len(NOITE) - 1, tom + (1 if meio else 0))])
    return imagem


def veus(imagem, sorteio):
    largura, altura = imagem.size
    for _ in range(max(3, largura // 120)):
        cx, cy = sorteio.uniform(0, largura), sorteio.uniform(altura * 0.15, altura * 0.6)
        comprimento, espessura = sorteio.uniform(60, 160), sorteio.uniform(3, 7)
        for x in range(int(cx - comprimento), int(cx + comprimento)):
            if not 0 <= x < largura:
                continue
            u = (x - cx) / comprimento
            meia = espessura * (1 - u * u)
            centro = cy + math.sin(u * 3 + cx) * 4
            for y in range(int(centro - meia), int(centro + meia) + 1):
                if 0 <= y < altura:
                    atual = NOITE.index(imagem.getpixel((x, y))) if imagem.getpixel((x, y)) in NOITE else 1
                    claro = 2 if abs(y - centro) < meia * 0.45 else 1
                    imagem.putpixel((x, y), NOITE[min(len(NOITE) - 1, atual + claro)])


def estrelas(imagem, sorteio, limite_y, livre):
    largura, altura = imagem.size
    for _ in range(largura * altura // 900):
        x, y = sorteio.randrange(largura), sorteio.randrange(int(altura * limite_y))
        if not livre(x, y):
            imagem.putpixel((x, y), OURO[sorteio.choice((2, 3, 3, 4, 5))])
    for _ in range(max(2, largura * altura // 22000)):
        x, y = sorteio.randrange(3, largura - 3), sorteio.randrange(3, int(altura * limite_y))
        braco = sorteio.choice((1, 1, 2))
        if livre(x, y):
            continue
        imagem.putpixel((x, y), OURO[5])
        for k in range(1, braco + 1):
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                imagem.putpixel((x + dx, y + dy), OURO[4 if k == 1 else 3])


def cristal(imagem, x, chao, alto, meia):
    largura = imagem.width
    topo = chao - alto
    for y in range(topo, chao + 1):
        largura_linha = meia * min(1, (y - topo) / max(1, alto * 0.45))
        for px in range(int(x - largura_linha), int(x + largura_linha) + 1):
            if not 0 <= px < largura:
                continue
            borda = abs(px - x) >= largura_linha - 1 or y == topo
            if borda and px <= x:
                cor = OURO[3] if y < topo + alto * 0.4 else OURO[2]
            elif borda:
                cor = OURO[1]
            elif px == x:
                cor = OURO[2] if y < topo + alto * 0.5 else NOITE[2]
            else:
                cor = NOITE[2] if px < x else NOITE[0]
            imagem.putpixel((px, y), cor)


def cristais(imagem, sorteio):
    largura, altura = imagem.size
    chao = altura - max(4, altura // 18)
    for x in range(largura):
        for y in range(chao, altura):
            imagem.putpixel((x, y), NOITE[0])
    x = sorteio.randint(-10, 30)
    while x < largura + 10:
        alto = sorteio.randint(altura // 10, altura // 5)
        meia = max(3, alto // 5)
        for lado in (-1, 1):
            if sorteio.random() < 0.7:
                menor = int(alto * sorteio.uniform(0.4, 0.65))
                cristal(imagem, x + lado * (meia + max(2, menor // 6)), chao, menor, max(2, menor // 5))
        cristal(imagem, x, chao, alto, meia)
        x += sorteio.randint(largura // 6, largura // 3)


def banner(nome, tamanho, escala, posicao, logo):
    largura, altura = -(-tamanho[0] // escala), -(-tamanho[1] // escala)
    sorteio = random.Random(nome)
    imagem = ceu(largura, altura, sorteio)
    veus(imagem, sorteio)
    logo_x = (largura - logo.width) // 2 if posicao == "centro" else largura - logo.width - largura // 20
    logo_y = (altura - logo.height) * 2 // 5

    def sob_a_logo(x, y):
        return logo_x - 4 <= x < logo_x + logo.width + 4 and logo_y - 4 <= y < logo_y + logo.height + 4

    estrelas(imagem, sorteio, 0.8, sob_a_logo)
    cristais(imagem, sorteio)
    imagem.paste(logo, (logo_x, logo_y), logo)
    ampliada = imagem.resize((largura * escala, altura * escala), Image.NEAREST)
    return ampliada.crop((0, 0) + tamanho)


def gerar_banners():
    simbolo = ler_grade(FONTE / "simbolo.txt")
    logo = desenhar(logo_horizontal(simbolo, ler_letras(FONTE / "letras.txt")), transparente=True)
    pasta = RAIZ / "banner"
    pasta.mkdir(exist_ok=True)
    for nome, (tamanho, escala, posicao) in BANNERS.items():
        banner(nome, tamanho, escala, posicao, logo).save(pasta / f"{nome}.png")


if __name__ == "__main__":
    gerar_banners()
