import pygame, numpy as np, random, time

PASTA = "corrida/"
MEDIR = False      
ESCALA = 4         
DISTANCIA = 60     
LONGE = 999        
DESCARTE = True    

pygame.init()
tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = tela.get_size()
L, A = W // ESCALA, H // ESCALA
sup = pygame.Surface((L, A))
fonte = pygame.font.Font(None, H // 16)
CEU, GRAMA, ASFALTO = (150, 200, 235), (70, 140, 60), (85, 85, 90)
CX, CY, FOCO = L / 2, A * 0.3, L * 0.6
pontos, vidas = 0, 3

def escrever(texto, linha):
    img = fonte.render(texto, True, (255, 255, 255), (0, 0, 0))
    tela.blit(img, (10, 10 + linha * fonte.get_height()))

luz = np.array([-0.4, 1.0, -0.6]) / np.linalg.norm([-0.4, 1.0, -0.6])

def abrir(nome):
    V, C, F = [], [], []
    for linha in open(PASTA + nome):
        p = linha.split()
        if p and p[0] == "v":
            V.append([float(t) for t in p[1:4]])
            C.append([float(t) for t in p[4:7]] or [0.8, 0.8, 0.8])
        elif p and p[0] == "f":
            i = [int(t.split("/")[0]) - 1 for t in p[1:]]
            for k in range(1, len(i) - 1):
                F.append((i[0], i[k], i[k + 1]))
    V, C, F = np.array(V), np.array(C), np.array(F)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a)
    n = n / np.linalg.norm(n, axis=1, keepdims=True)
    brilho = 0.45 + 0.55 * np.clip(n @ luz, 0, 1)
    cor = C[F].mean(axis=1) * 255 * brilho[:, None]
    return V, F, cor

JOGADOR, BALA = abrir("jogador.obj"), abrir("bala.obj")
AZUL, VERMELHO = abrir("robo_azul.obj"), abrir("robo_vermelho.obj")
ARVORE, ARVORE_SIMPLES = abrir("arvore.obj"), abrir("arvore_simples.obj")
FAIXA = abrir("faixa.obj")

CAM = np.array([0.0, 3.0, -6.0])
jogador = [JOGADOR, np.array([0.0, 0.0, 0.0]), "jogador"]
objetos = [jogador]

def projetar(P):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    col = CX + FOCO * x / z
    lin = CY - FOCO * y / z
    return np.stack([col, lin], axis=1)

def desenhar_mundo(sup):
    sup.fill(CEU)
    pygame.draw.rect(sup, GRAMA, (0, CY, L, A - CY))
    pista = np.array([[-3, 0, 0.5], [3, 0, 0.5], [3, 0, DISTANCIA], [-3, 0, DISTANCIA]])
    pygame.draw.polygon(sup, ASFALTO, projetar(pista - [0, CAM[1], 0]).tolist())
    Vs, Fs, Cs, base = [], [], [], 0
    for o in objetos:
        if o[1][2] - CAM[2] > DISTANCIA:
            continue
        m = o[0]
        if o[2] == "arvore" and o[1][2] - CAM[2] > LONGE:
            m = ARVORE_SIMPLES
        V, F, cor = m
        Vs.append(V + o[1] - CAM)
        Fs.append(F + base)
        Cs.append(cor)
        base += len(V)
    V, F, cor = np.concatenate(Vs), np.concatenate(Fs), np.concatenate(Cs)
    T = projetar(V)[F]
    z = V[:, 2][F]
    fica = z.min(axis=1) > 0.5
    area = ((T[:, 1, 0] - T[:, 0, 0]) * (T[:, 2, 1] - T[:, 0, 1])
            - (T[:, 2, 0] - T[:, 0, 0]) * (T[:, 1, 1] - T[:, 0, 1]))
    if DESCARTE:
        fica = fica & (area > 0)
    T, cor, zm = T[fica], cor[fica], z[fica].mean(axis=1)
    nevoa = (np.clip(zm / DISTANCIA, 0, 1) ** 2)[:, None]
    cor = cor * (1 - nevoa) + np.array(CEU) * nevoa
    ordem = np.argsort(-zm)
    T, cor = T.tolist(), cor.astype(int).tolist()
    for i in ordem:
        pygame.draw.polygon(sup, cor[i], T[i])
    return len(T)

VEL = 12  
alvo, andou, prox_arvore, prox_faixa = 0, 0.0, 0.0, 0.0
random.seed(2026)

def plantar(z):
    for lado in (-1, 1):
        x = lado * random.uniform(5, 9)
        objetos.append([ARVORE, np.array([x, 0.0, z]), "arvore"])

for z in range(4, 100, 8):
    plantar(z)
for z in range(0, 100, 5):
    objetos.append([FAIXA, np.array([-1.0, 0.0, z]), "faixa"])
    objetos.append([FAIXA, np.array([1.0, 0.0, z]), "faixa"])

def tocar(esquerda):
    global alvo
    if esquerda:
        alvo = max(alvo - 1, -1)
    else:
        alvo = min(alvo + 1, 1)

def atualizar(dt):
    global andou, prox_arvore, prox_faixa
    andou += VEL * dt
    for o in objetos:
        if o[2] in ("arvore", "faixa", "robo"):
            o[1][2] -= VEL * dt
    jogador[1][0] += (2 * alvo - jogador[1][0]) * min(1, 10 * dt)
    if andou >= prox_arvore:
        plantar(100)
        prox_arvore += 8
    if andou >= prox_faixa:
        objetos.append([FAIXA, np.array([-1.0, 0.0, 100]), "faixa"])
        objetos.append([FAIXA, np.array([1.0, 0.0, 100]), "faixa"])
        prox_faixa += 5
    objetos[:] = [o for o in objetos if o[1][2] > -4]

prox_robo, recarga = 0.0, 0.0
ALCANCE = 20  

def combate(dt):
    global prox_robo, recarga, pontos, vidas, alvo
    if vidas <= 0:
        return
    if andou >= prox_robo:
        x = float(2 * random.choice((-1, 0, 1)))
        if random.random() < 0.35:
            objetos.append([VERMELHO, np.array([x, 0.0, 100.0]), "robo", 1, "vermelho"])
        else:
            objetos.append([AZUL, np.array([x, 0.0, 100.0]), "robo", 3, "azul"])
        prox_robo += 12
    recarga -= dt
    if recarga <= 0:
        objetos.append([BALA, jogador[1] + [0.42, 1.1, 1.0], "bala"])
        recarga = 0.25
    robos = [o for o in objetos if o[2] == "robo"]
    balas = [o for o in objetos if o[2] == "bala"]
    for r in robos:
        r[1][2] -= 4 * dt
    for b in balas:
        b[1][2] += 40 * dt
        for r in robos:
            if r[3] > 0 and abs(b[1][0] - r[1][0]) < 0.8 and abs(b[1][2] - r[1][2]) < 1.5:
                b[1][2] = 999
                if r[4] == "azul":
                    r[3] -= 1
                    if r[3] == 0:
                        pontos += 10
    for r in robos:
        if r[3] > 0 and r[1][2] < 0.8 and abs(r[1][0] - jogador[1][0]) < 1.2:
            r[3] = 0
            if not MEDIR:
                vidas -= 1
    objetos[:] = [o for o in objetos if not (o[2] == "robo" and o[3] == 0)
                  and not (o[2] == "bala" and o[1][2] > ALCANCE)]
    if MEDIR:
        perigo = [round(r[1][0] / 2) for r in robos if r[4] == "vermelho" and 0 < r[1][2] < 15]
        livres = [f for f in (-1, 0, 1) if f not in perigo]
        azuis = [r for r in robos if r[4] == "azul" and r[3] > 0 and r[1][2] > 3
                 and round(r[1][0] / 2) in livres]
        if azuis:
            alvo = round(min(azuis, key=lambda r: r[1][2])[1][0] / 2)
        elif alvo not in livres and livres:
            alvo = min(livres, key=lambda f: abs(f - alvo))

def resultado(tempos, tris_lista):
    media = sum(tempos) / len(tempos)
    acima = sum(1 for t in tempos if t > 33.3)
    linhas = [f"média {media:.1f} ms ({1000 / media:.0f} qps)",
              f"pior quadro {max(tempos):.1f} ms",
              f"acima de 33,3 ms: {acima} de {len(tempos)} quadros",
              f"triângulos por quadro: {sum(tris_lista) // len(tris_lista)}",
              f"pontos {pontos}",
              "toque para sair"]
    with open(PASTA + "resultado.txt", "a") as arq:
        arq.write(f"ESCALA={ESCALA} DISTANCIA={DISTANCIA} LONGE={LONGE} DESCARTE={DESCARTE}\n")
        arq.write("\n".join(linhas[:-1]) + "\n\n")
    tela.fill((0, 0, 0))
    for i, t in enumerate(linhas):
        escrever(t, i)
    pygame.display.flip()
    while True:
        ev = pygame.event.wait()
        if ev.type in (pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            return

def rodar():
    tempos, tris_lista = [], []
    antes = time.perf_counter()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_AC_BACK, pygame.K_ESCAPE):
                return
            if ev.type == pygame.MOUSEBUTTONDOWN:
                tocar(ev.pos[0] < W / 2)
        agora = time.perf_counter()
        dt = agora - antes
        antes = agora
        if MEDIR:
            dt = 1 / 30
        t0 = time.perf_counter()
        atualizar(dt)
        combate(dt)
        tris = desenhar_mundo(sup)
        pygame.transform.scale(sup, (W, H), tela)
        ms = (time.perf_counter() - t0) * 1000
        tempos.append(ms)
        tris_lista.append(tris)
        media = sum(tempos[-30:]) / len(tempos[-30:])
        qps = 1000 / media
        escrever(f"{media:.1f} ms {qps:.0f} qps {tris} triângulos", 0)
        escrever(f"pontos {pontos} vidas {vidas}", 1)
        pygame.display.flip()
        if MEDIR and len(tempos) == 600:
            resultado(tempos, tris_lista)
            return

rodar()
pygame.quit()