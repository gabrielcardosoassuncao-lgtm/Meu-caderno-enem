from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_preta(imagem, cor_alvo, tolerancia=15): 
    """
    Encontra posições onde há uma faixa horizontal da cor especificada,
    percorrendo o último pixel da direita e considerando a margem de erro na altura.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    y = 0
    while y < altura:
        # Conta a altura consecutiva da faixa que corresponde à cor alvo
        altura_faixa_atual = 0
        while y + altura_faixa_atual < altura:
            # ALTERADO: Analisa exatamente o ÚLTIMO pixel da direita (largura - 1)
            pixel = pixels[largura - 1, y + altura_faixa_atual]  
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor está dentro da tolerância
            if (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia):
                altura_faixa_atual += 1
            else:
                break
        
        # ALTERADO: Procura padrão de 19px com margem de erro de 2px para mais/menos (17 a 21 pixels)
        if 17 <= altura_faixa_atual <= 21:
            # ALTERADO: Corta exatamente 23 pixels antes de começar o padrão
            posicao_corte = y - 23  
            if posicao_corte < 0:  # Evita posições negativas no topo da imagem
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Faixa preta encontrada (altura: {altura_faixa_atual}px) em y={y}, definindo corte em y={posicao_corte}")
            
            # Pula a faixa inteira encontrada para continuar a busca
            y += altura_faixa_atual
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando ANTES das faixas sem descartar pixels
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Busca as posições de corte com a nova lógica
    posicoes_corte = encontrar_faixa_preta(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa correspondente encontrada na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção até o ponto de corte definido (23 pixels antes do padrão)
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # ALTERADO: A próxima seção começa exatamente onde a anterior terminou.
        # Isso garante que os 23 pixels e a faixa preta permaneçam intactos no início do próximo bloco.
        posicao_anterior = posicao_corte
    
    # Corta a seção final da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "./inteiras/pagina_enem_5.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "5_cortada"           # Substitua pelo nome da pasta de saída desejada

    # ALTERADO: Definida a cor RGB (0, 0, 0) diretamente, conforme solicitado
    cor_do_padrao = (0, 0, 0) 
    print(f"Cor alvo configurada: RGB {cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")