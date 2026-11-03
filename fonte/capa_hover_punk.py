from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from gerar import OURO, RAIZ, cor_15_bits

JOGO = Path(__file__).resolve().parents[2] / "hover-punk" / "Assets" / "_Project" / "Art"
CAMADAS = ["00_ceu", "01_longe", "02_neblina", "03_meio", "03_meio_glow", "04_perto", "04_perto_glow", "05_chao", "06_frente"]
LARGURA, ALTURA, ESCALA = 315, 250, 2
RECORTE_X, RECORTE_Y = 70, 96
ROSA, CIANO, SOMBRA = cor_15_bits((255, 63, 211)), cor_15_bits((61, 242, 255)), cor_15_bits((20, 8, 40))


def cenario():
    fase = Image.new("RGBA", (768, 432))
    for nome in CAMADAS:
        fase.alpha_composite(Image.open(JOGO / "Backgrounds" / "Stage01" / f"{nome}.png").convert("RGBA"))
    return fase.crop((RECORTE_X, RECORTE_Y, RECORTE_X + LARGURA, RECORTE_Y + ALTURA))


def texto_com_contorno(imagem, posicao, texto, fonte, cor, contorno, sombra):
    desenho = ImageDraw.Draw(imagem)
    desenho.fontmode = "1"
    x, y = posicao
    desenho.text((x + 2, y + 2), texto, font=fonte, fill=sombra)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            desenho.text((x + dx, y + dy), texto, font=fonte, fill=contorno)
    desenho.text((x, y), texto, font=fonte, fill=cor)


def centralizado(fonte, texto):
    esquerda, _, direita, _ = fonte.getbbox(texto)
    return (LARGURA - (direita - esquerda)) // 2


def capa():
    imagem = cenario()
    titulo = ImageFont.truetype(str(JOGO / "Fonts" / "PressStart2P.ttf"), 24)
    selo = ImageFont.truetype(str(JOGO / "Fonts" / "Silkscreen.ttf"), 8)
    texto_com_contorno(imagem, (centralizado(titulo, "HOVER PUNK"), 12), "HOVER PUNK", titulo, ROSA, SOMBRA, CIANO)
    mensageiro = Image.open(JOGO / "Character" / "Player" / "Courier" / "Courier_Idle_0.png").convert("RGBA")
    mensageiro = mensageiro.resize((mensageiro.width * 2, mensageiro.height * 2), Image.NEAREST)
    imagem.alpha_composite(mensageiro, ((LARGURA - mensageiro.width) // 2, ALTURA - mensageiro.height - 2))
    marca = "MAGIN DREAMERS"
    texto_com_contorno(imagem, (LARGURA - selo.getbbox(marca)[2] - 6, ALTURA - 14), marca, selo, cor_15_bits(OURO[4]), SOMBRA, SOMBRA)
    imagem = imagem.convert("RGB")
    imagem.resize((LARGURA * ESCALA, ALTURA * ESCALA), Image.NEAREST).save(RAIZ / "capa" / "hover-punk-630x500.png")


if __name__ == "__main__":
    capa()
