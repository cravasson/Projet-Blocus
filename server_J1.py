import asyncio
import pickle
import os
import sys


# ====================================================================================================
#                             Comment lancer le jeu : 
# 1- Ouvrir autant de terminal que de joueurs dans le dossier des fichiers .py 
# 2- Copier les commandes suivantes en fonction du nombre de joueurs (1 commande par terminal):
# & "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.11.exe" server_J1.py   OBLIGATOIRE (Terminal1)
# & "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.11.exe" client_J2.py    2 Joueurs  (Terminal2)
# & "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.11.exe" client_J3.py    3 joueurs  (Terminal3)
# & "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.11.exe" client_J4.py    4 joueurs  (Terminal4)
# ====================================================================================================

# =============================================================================
# 1. IMPORTS
# =============================================================================
try:
    import blokus_multi as bk
except ImportError:
    sys.exit("ERREUR CRITIQUE : 'blokus_multi.py' introuvable.")

# =============================================================================
# 2. CONFIGURATION RÉSEAU
# =============================================================================
HOST = '127.0.0.1'
PORT = 8888

clients_connectes = []
nb_joueurs_config = 0
noms_des_joueurs_finaux = [] # Pour stocker les 4 noms (Bleu, Jaune, Rouge, Vert)
event_start = asyncio.Event()

# =============================================================================
# 3. GESTION CONNEXIONS
# =============================================================================
async def handle_client(reader, writer):
    global clients_connectes
    clients_connectes.append((reader, writer))
    print(f"\n[+] Client {len(clients_connectes)} connecté.")
    
    if len(clients_connectes) == nb_joueurs_config - 1:
        print("\n>>> TOUS LES JOUEURS SONT LÀ ! <<<")
        event_start.set()

    await event_start.wait()
    try: await asyncio.Future() 
    except: pass

# =============================================================================
# 4. INITIALISATION (RÈGLES ET NOMS)
# =============================================================================
async def main():
    global nb_joueurs_config, noms_des_joueurs_finaux, grille
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # --- TEXTE DES RÈGLES ---
    print("=== BLOKUS SERVEUR MULTIJOUEUR ===\nREGLES DU JEU :\n\n" \
    "1- MATERIEL:\nLe jeu se compose des éléments suivants:" \
    "Un plateau de jeu de 400 cases.\n" \
    "84 pièces (21 pièces dans chacune des quatre couleurs ). \n" \
    "Chacune des 21 pièces est de forme différente: \nIl y a 1 pièce d’un carré," \
    "1 pièce à deux carrés, 2 pièces à trois carrés, 5 pièces à quatre carrés, 12" \
    "pièces à cinq carré. \n\n" \
    "2- BUT DU JEU:\nPour chaque joueur, placer ses 21 pièces sur le plateau.\n\n" \
    "3- DEROULEMENT D'UNE PARTIE:\n" \
    "L’ordre dans lequel on joue est le suivant (Standard):\n" \
    "Bleu, Jaune, Rouge, Vert.\n" \
    "Le premier joueur place la première pièce de son choix sur le plateau de telle sorte que celle-ci recouvre une case d’angle du plateau.\n" \
    "Les autres joueurs jouent à tour de rôle et placent leur première pièce de la même manière.\n" \
    "Pour les tours suivants, chaque nouvelle pièce posée doit toucher une pièce de la même couleur par un ou plusieurs coins et jamais par les cotés.\n" \
    "En revanche, les pièces de couleur différente peuvent se toucher par les cotés.\n\n" \
    "4- FIN DE LA PARTIE:\n" \
    "Lorsqu’un joueur est bloqué et ne peut plus placer de pièce, il est obligé de passer son tour.\n" \
    "Les autres joueurs poursuivent en conservant le même ordre de jeu.\nLorsque tous les joueurs sont bloqués, chacun compte" \
    "le nombre de carrés qu’il n’a pu placer sur le plateau et calcule son score:\n" \
    "-1 point par carré non posé.\n" \
    "+15 points si les 21 pièces ont été posées.\n" \
    "+20 points si les 21 pièces ont été posées.\n\n\n")

    # --- CHOIX DU NOMBRE DE JOUEURS ---
    while True:
        try:
            nb = int(input("Combien de joueurs humains au total (2, 3 ou 4) ? : "))
            if 2 <= nb <= 4:
                nb_joueurs_config = nb
                break
        except: pass

    print("\n--- CONFIGURATION DES NOMS ---")
    
    # --- CONFIGURATION DES NOMS SELON LE NOMBRE DE JOUEURS ---
    if nb_joueurs_config == 2:
        print("Mode 2 Joueurs : Chaque joueur prend 2 couleurs (croisées).")
        nom1 = input("Nom du Joueur 1 (Sera Bleu & Rouge) : ")
        nom2 = input("Nom du Joueur 2 (Sera Jaune & Vert) : ")
        # On remplit la liste des 4 couleurs : [Bleu, Jaune, Rouge, Vert]
        noms_des_joueurs_finaux = [nom1, nom2, nom1, nom2]

    elif nb_joueurs_config == 3:
        print("Mode 3 Joueurs : Le Vert est 'Neutre' et change de main.")
        n1 = input("Nom du Joueur 1 (Bleu) : ")
        n2 = input("Nom du Joueur 2 (Jaune) : ")
        n3 = input("Nom du Joueur 3 (Rouge) : ")
        noms_des_joueurs_finaux = [n1, n2, n3, "NEUTRE"]

    else:
        print("Mode 4 Joueurs : Classique.")
        n1 = input("Nom du Joueur 1 (Bleu)  : ")
        n2 = input("Nom du Joueur 2 (Jaune) : ")
        n3 = input("Nom du Joueur 3 (Rouge) : ")
        n4 = input("Nom du Joueur 4 (Vert)  : ")
        noms_des_joueurs_finaux = [n1, n2, n3, n4]

    grille = bk.init_grille(20, 20)
    print(f"\nServeur lancé sur {HOST}:{PORT}")
    print(f"En attente de {nb_joueurs_config - 1} client(s)...")
    
    server = await asyncio.start_server(handle_client, HOST, PORT)
    await asyncio.gather(server.serve_forever(), boucle_jeu())

# =============================================================================
# 5. BOUCLE DE JEU
# =============================================================================
async def boucle_jeu():
    global grille, noms_des_joueurs_finaux
    
    await event_start.wait()
    await asyncio.sleep(1)

    # Initialisation des JOUEURS avec les NOMS choisis
    # Ordre strict : Bleu, Jaune, Rouge, Vert
    j_bleu  = bk.Joueur(noms_des_joueurs_finaux[0], "🟦", bk.PIECES_FORMES)
    j_jaune = bk.Joueur(noms_des_joueurs_finaux[1], "🟨", bk.PIECES_FORMES)
    j_rouge = bk.Joueur(noms_des_joueurs_finaux[2], "🟥", bk.PIECES_FORMES)
    j_vert  = bk.Joueur(noms_des_joueurs_finaux[3], "🟩", bk.PIECES_FORMES)
    
    ordre_jeu = [j_bleu, j_jaune, j_rouge, j_vert]
    
    tour_index = 0
    nb_tours_vert = 0 
    
    # Compteur pour savoir si TOUT LE MONDE est bloqué (4 passes d'affilée)
    compteur_passes = 0
    
    # NOUVEAU : Compteur global de tours
    nb_tours_global = 1

    while True:
        # VERIFICATION DE FIN DE PARTIE
        if compteur_passes >= 4:
            break # Sortie de la boucle infinie -> Direction l'affichage des scores

        joueur_actuel = ordre_jeu[tour_index]
        qui_controle = -1 
        info_txt = ""

        # --- LOGIQUE QUI TIENT LA MANETTE ---
        if nb_joueurs_config == 2:
            if tour_index == 0 or tour_index == 2: qui_controle = 0 # Serveur (J1)
            else: qui_controle = 1 # Client (J2)
                
        elif nb_joueurs_config == 3:
            if joueur_actuel == j_bleu:   qui_controle = 0
            elif joueur_actuel == j_jaune: qui_controle = 1
            elif joueur_actuel == j_rouge: qui_controle = 2
            elif joueur_actuel == j_vert:
                qui_controle = nb_tours_vert % 3
                nom_qui_joue = noms_des_joueurs_finaux[qui_controle]
                info_txt = f"(Le Vert est joué par {nom_qui_joue})"
                nb_tours_vert += 1
        else:
            qui_controle = tour_index

        print(f"\n--- TOUR {nb_tours_global} | DE : {joueur_actuel.nom} ({joueur_actuel.emoji}) ---")
        if info_txt: print(info_txt)

        # SERVEUR JOUE
        if qui_controle == 0:
            choix_valide = False
            msg = f"A toi de jouer {joueur_actuel.nom} !"
            while not choix_valide:
                # Ajout de numero_tour
                choix = bk.saisir_choix_interactif(grille, joueur_actuel, msg, info_txt, numero_tour=nb_tours_global)
                
                # S'il passe son tour (99 ou Echap)
                if choix == -1 or choix == 99: 
                     print("On passe notre tour.")
                     compteur_passes += 1
                     choix_valide = True
                
                # Jouer une pièce
                elif 0 <= choix < len(joueur_actuel.main) and not joueur_actuel.main[choix].posee:
                    # Ajout de numero_tour
                    if bk.deplacer_et_poser(grille, joueur_actuel.main[choix], joueur_actuel, info_txt, numero_tour=nb_tours_global):
                        # Pièce posée -> On remet le compteur de passes à 0
                        compteur_passes = 0
                        choix_valide = True
                    else: msg = "Placement impossible"
                else: msg = "Pièce invalide"
            
            print("Coup validé. Envoi de la maj...")

        # CLIENT JOUE
        else:
            idx_client = qui_controle - 1
            if idx_client < len(clients_connectes):
                reader, writer = clients_connectes[idx_client]
                try:
                    # Pour détecter si le client a passé, on compte ses pièces posées AVANT
                    nb_pieces_avant = sum(1 for p in joueur_actuel.main if p.posee)
                    
                    # MODIFICATION IMPORTANTE : ON ENVOIE 4 ELEMENTS MAINTENANT (AVEC LE TOUR)
                    data_pack = (grille, joueur_actuel, info_txt, nb_tours_global)
                    writer.write(pickle.dumps(data_pack))
                    await writer.drain()
                    
                    data = await reader.read(100000)
                    if not data: break
                    
                    nouvelle_grille, joueur_maj = pickle.loads(data)
                    grille = nouvelle_grille
                    ordre_jeu[tour_index] = joueur_maj # Maj inventaire
                    
                    # Maj des variables locales
                    if tour_index == 0: j_bleu = joueur_maj
                    elif tour_index == 1: j_jaune = joueur_maj
                    elif tour_index == 2: j_rouge = joueur_maj
                    elif tour_index == 3: j_vert = joueur_maj
                    
                    # Vérification APRES
                    nb_pieces_apres = sum(1 for p in joueur_maj.main if p.posee)
                    
                    if nb_pieces_apres == nb_pieces_avant:
                        print(f"{joueur_actuel.nom} a PASSÉ son tour.")
                        compteur_passes += 1
                    else:
                        print(f"Coup reçu de {joueur_actuel.nom}.")
                        compteur_passes = 0

                except Exception as e:
                    print(f"Erreur client : {e}")
                    break

        tour_index = (tour_index + 1) % 4
        
        # SI LE TOUR INDEX REVIENT A 0 (C'est de nouveau au Bleu), ON INCREMENTE LE TOUR GLOBAL
        if tour_index == 0:
            nb_tours_global += 1
    
    # === FIN DE PARTIE ===
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*50)
    print("       🏁  FIN DE LA PARTIE  🏁       ")
    print(f"       Nombre total de tours : {nb_tours_global-1}")
    print("="*50 + "\n")
    
    # Calcul des scores
    scores_finaux = {}
    
    for joueur_coul in ordre_jeu:
        points = bk.calculer_score(joueur_coul)
        
        # On additionne les points au NOM du joueur (pour gérer le mode 2 joueurs)
        if joueur_coul.nom in scores_finaux:
            scores_finaux[joueur_coul.nom] += points
        else:
            scores_finaux[joueur_coul.nom] = points
            
        print(f" > Couleur {joueur_coul.emoji} ({joueur_coul.nom}) : {points} pts")
    
    print("-" * 50)
    print("CLASSEMENT FINAL :")
    
    # Tri des scores
    classement = sorted(scores_finaux.items(), key=lambda x: x[1], reverse=True)
    
    for i, (nom, score) in enumerate(classement):
        medaille = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        print(f" {medaille} {nom} : {score} points")
        
    print("\nMerci d'avoir joué !!!\n" \
    "\nRéalisé par Célia et José\n")
    print("="*50)
    input("Appuyez sur Entrée pour fermer...")
    sys.exit()

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())