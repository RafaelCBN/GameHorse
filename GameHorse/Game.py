import pygame
import random
import sys
import os

pygame.init()

# Cria janela
width, height = 800, 1000
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Corrida de Cavalos")

# Função para carregar imagens
def carregar_imagem(nome_arquivo, largura_max=None, altura_max=None):
    if os.path.exists(nome_arquivo):
        imagem = pygame.image.load(nome_arquivo).convert_alpha()
        if largura_max and altura_max:
            imagem = pygame.transform.scale(imagem, (largura_max, altura_max))
        return imagem
    else:
        print(f"Erro: A imagem '{nome_arquivo}' não foi encontrada no diretório.")
        sys.exit()

# Carregar fundo
fundo = carregar_imagem('fundo.png')
screen.blit(fundo, (0, 0))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Carregar imagens de pulo com redimensionamento
pulando1_image = carregar_imagem('pulando1.png', 100, 100)
pulando2_image = carregar_imagem('pulando2.png', 100, 100)
pulando3_image = carregar_imagem('pulando3.png', 100, 100)

# Carregar imagem de obstáculo com redimensionamento para 100x100 pixels
obstaculo_image = carregar_imagem('obstaculo.png', 100, 100)

# Carregar imagem da linha de chegada
linha_chegada_image = carregar_imagem('chegada.jpg')
linha_chegada_image = pygame.transform.scale(linha_chegada_image, (linha_chegada_image.get_width(), 50))  # Redimensionar a altura para 50 pixels

# Carregar imagens dos cavalos
cavalo_images = []
for i in range(1, 12):
    cavalo_images.append(carregar_imagem(f'cavalo_{i}.jpg'))

# Carregar imagem de cavalo caído com redimensionamento
caido_image = carregar_imagem('caido.jpg', 130, 100)

# Classe Cavalo com obstáculos
class Cavalo:
    def __init__(self, nome, imagens, velocidade, stamina, obstaculos):
        self.nome = nome
        self.imagens = imagens
        self.image_index = 0
        self.velocidade = velocidade
        self.velocidade_original = velocidade  
        self.stamina = stamina
        self.posicao = 0
        self.cansaco = 0
        self.obstaculos = obstaculos
        self.qualificacao = 0
        self.caido = False  
        self.assustado = False  
        self.pulando = False  
        self.pulando_countdown = 0  

    def correr(self):
        if self.caido:
            return

        if random.random() < 0.003:  # 1% de chance de cair
            self.caido = True
            return

        if self.cansaco < self.stamina:
            self.posicao += self.velocidade
            self.cansaco += 1
        else:
            self.posicao += self.velocidade // 2
            self.cansaco = max(0, self.cansaco - 1)

        # Verifica se passou por um obstáculo
        for obstaculo in self.obstaculos:
            if self.posicao >= obstaculo['posicao'] - 30 and self.posicao <= obstaculo['posicao'] + 30:  # Ajusta a proximidade para iniciar o pulo
                self.pulando = True
                self.pulando_countdown = 20  # Tempo em iterações para manter o pulo ativo
                obstaculo['passou'] = True
            elif self.posicao >= obstaculo['posicao'] + 30:
                self.pulando = False

        # Controle do pulo
        if self.pulando_countdown > 0:
            self.pulando_countdown -= 1
        else:
            self.pulando = False

        # Se estiver assustado, reduzir a posição gradualmente
        if self.assustado:
            if self.posicao > 0:
                self.posicao -= 1

        # Atualizar a imagem do cavalo
        self.image_index = (self.image_index + 1) % len(self.imagens)

    def get_qualificacao(self):
        return self.qualificacao

# Gerar velocidades justas
def gerar_velocidades_justas(num_cavalos, min_vel, max_vel):
    velocidades = []
    for _ in range(num_cavalos):
        velocidades.append(random.randint(min_vel, max_vel))
    return velocidades

# Gerar obstáculos para cada cavalo
def gerar_obstaculos(num_cavalos):
    obstaculos = []
    for i in range(num_cavalos):
        posicoes_obstaculos = random.sample(range(100, width - 100), 3)  # 3 obstáculos por cavalo
        obstaculos_cavalo = []
        for posicao in posicoes_obstaculos:
            obstaculos_cavalo.append({'posicao': posicao, 'dificuldade': random.randint(2, 5), 'passou': False})
        obstaculos.append(obstaculos_cavalo)
    return obstaculos

num_cavalos = 7
velocidades = gerar_velocidades_justas(num_cavalos, 4, 8)
obstaculos = gerar_obstaculos(num_cavalos)

# Criar os cavalos
cavalos = []
for i in range(num_cavalos):
    cavalo = Cavalo(f"Cavalo {i+1}", cavalo_images, velocidades[i], random.randint(40, 100), obstaculos[i])
    cavalos.append(cavalo)

fonte = pygame.font.Font(None, 36)
running = False
vencedor = None

# Contagem regressiva
for i in range(3, 0, -1):
    screen.fill(BLACK)
    texto_contagem = fonte.render(f"{i}", True, WHITE)
    screen.blit(texto_contagem, (width // 2 - texto_contagem.get_width() // 2, height // 2 - texto_contagem.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(1000)

screen.fill(BLACK)
texto_vai = fonte.render("Vai!", True, WHITE)
screen.blit(texto_vai, (width // 2 - texto_vai.get_width() // 2, height // 2 - texto_vai.get_height() // 2))
pygame.display.flip()
pygame.time.delay(1000)

# Iniciar a corrida
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    # Desenhar fundo
    screen.blit(fundo, (0, 0))

    # Desenhar obstáculos para cada cavalo
    for idx, cavalo in enumerate(cavalos):
        for obstaculo in cavalo.obstaculos:
            screen.blit(obstaculo_image, (obstaculo['posicao'], (idx + 1) * 100 + 10))

    # Desenhar linha de chegada
    screen.blit(linha_chegada_image, (width - 50, 0))

    # Mover e desenhar cavalos
    for idx, cavalo in enumerate(cavalos):
        cavalo.correr()
        if cavalo.posicao >= width - 50:
            vencedor = cavalo.nome
            running = False

        # Desenhar cavalo
        if cavalo.caido:
            cavalo_rect = caido_image.get_rect(topleft=(cavalo.posicao, (idx + 1) * 100 + 10))
            screen.blit(caido_image, cavalo_rect.topleft)
        elif cavalo.pulando:
            # Desenha o pulo
            if cavalo.pulando_countdown >= 15:
                pulo_rect = pulando1_image.get_rect(midbottom=(cavalo.posicao + cavalo.imagens[cavalo.image_index].get_width() // 2, (idx + 1) * 100 + 10))
                screen.blit(pulando1_image, pulo_rect.bottomleft)
            elif cavalo.pulando_countdown >= 10:
                pulo_rect = pulando2_image.get_rect(midbottom=(cavalo.posicao + cavalo.imagens[cavalo.image_index].get_width() // 2, (idx + 1) * 100 + 10))
                screen.blit(pulando2_image, pulo_rect.bottomleft)
            else:
                pulo_rect = pulando3_image.get_rect(midbottom=(cavalo.posicao + cavalo.imagens[cavalo.image_index].get_width() // 2, (idx + 1) * 100 + 10))
                screen.blit(pulando3_image, pulo_rect.bottomleft)
        else:
            cavalo_rect = cavalo.imagens[cavalo.image_index].get_rect(topleft=(cavalo.posicao, (idx + 1) * 100 + 10))
            screen.blit(cavalo.imagens[cavalo.image_index], cavalo_rect.topleft)

    pygame.display.flip()
    pygame.time.delay(100)

#vencedor
screen.fill(BLACK)
texto_vencedor = fonte.render(f"Vencedor: {vencedor}", True, WHITE)
screen.blit(texto_vencedor, (width // 2 - texto_vencedor.get_width() // 2, height // 2 - texto_vencedor.get_height() // 2))
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
