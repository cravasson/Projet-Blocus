import os
import msvcrt
import copy
import sys

# ====================================================================================================
#                                 Comment lancer le jeu : 
# 1- Ouvrir un terminal dans le dossier des fichiers .py 
# 2- Copier cette ligne de code dans le terminal: 
#
#            & "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.11.exe" Blokus_2J.py
#
# ====================================================================================================     



# =============================================================================
# 1. CONSTANTES & CONFIGURATION
# =============================================================================

VIDE_STR = " . "
LARGEUR_VISUELLE_BLOC = 3

# =============================================================================
# 2. CLASSES (PIÈCE ET JOUEUR)
# =============================================================================

class Piece:
    def __init__(self, forme):
        self.forme = forme
        self.posee = False

    def pivoter(self):
        # Rotation de la pièce à 90 degrés
        self.forme = [list(row) for row in zip(*self.forme[::-1])]

class Joueur:
    def __init__(self, nom, emoji, formes_disponibles):
        self.nom = nom
        self.emoji = emoji
        self.main = [Piece(copy.deepcopy(f)) for f in formes_disponibles]
        self.premier_tour = True
    
    def recuperer_lignes_inventaire(self):
        lignes = []
        lignes.append(f"=== INVENTAIRE DE {self.nom} {self.emoji} ===")
        
        dispo = [i for i in range(len(self.main)) if not self.main[i].posee]
        
        # Affichage par rangées de 5 pièces
        for i in range(0, len(dispo), 5):
            groupe = dispo[i:i+5]
            
            txt_num = ""
            for num in groupe:
                txt_num += f"n°{num:<11} " 
            lignes.append(txt_num)
            
            for l in range(5): 
                ligne_piece = ""
                for num in groupe:
                    p = self.main[num]
                    bloc_rendu = ""
                    if l < len(p.forme):
                        for cellule in p.forme[l]:
                            bloc_rendu += (self.emoji + " ") if cellule == 1 else "   "
                    
                    len_visuelle = calcul_longueur_visuelle(bloc_rendu)
                    padding = 14 - len_visuelle
                    ligne_piece += bloc_rendu + (" " * padding)
                lignes.append(ligne_piece)
            lignes.append("-" * 60)
        return lignes

# =============================================================================
# 3. MOTEUR GRAPHIQUE (RENDU DE LA GRILLE)
# =============================================================================

def calcul_longueur_visuelle(chaine):
    longueur = 0
    for char in chaine:
        if ord(char) > 1000: 
            longueur += 2
        else:
            longueur += 1
    return longueur

def init_grille(nb_ligne, nb_colonne):
    return [[0 for _ in range(nb_colonne)] for _ in range(nb_ligne)]

def preparer_rendu_grille(grille_base, piece=None, pl=0, pc=0, joueur=None):
    nb_l = len(grille_base)
    nb_c = len(grille_base[0])
    rendu = [row[:] for row in grille_base]

    # Incrustation de la pièce (prévisualisation)
    if piece and joueur:
        for l in range(len(piece.forme)):
            for c in range(len(piece.forme[0])):
                if piece.forme[l][c] == 1:
                    target_l, target_c = pl + l, pc + c
                    if 0 <= target_l < nb_l and 0 <= target_c < nb_c:
                        if rendu[target_l][target_c] != 0:
                            rendu[target_l][target_c] = -1 
                        else:
                            rendu[target_l][target_c] = joueur.emoji

    lignes_grille = []
    
    header = "    " 
    for j in range(nb_c):
        header += f"{j:^3}"
    lignes_grille.append(header)
    lignes_grille.append("   ┌" + "───" * nb_c + "┐")
    
    for i in range(nb_l):
        ligne_str = f"{i:2} │" 
        for j in range(nb_c):
            val = rendu[i][j]
            if val == 0:
                ligne_str += VIDE_STR
            elif val == -1:
                ligne_str += "❌ "
            elif isinstance(val, str): 
                ligne_str += val + " " 
        ligne_str += "│"
        lignes_grille.append(ligne_str)
        
    lignes_grille.append("   └" + "───" * nb_c + "┘")
    return lignes_grille

# =============================================================================
# 4. INTERFACE UTILISATEUR (SPLIT SCREEN)
# =============================================================================

# AJOUT DE numero_tour
def afficher_interface_complete(grille, joueur, piece_active=None, l=0, c=0, mode_selection=True, message_erreur="", saisie_en_cours="", numero_tour=1):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    lignes_g = preparer_rendu_grille(grille, piece_active, l, c, joueur)
    
    # AFFICHAGE DU TOUR
    lignes_droite = []
    lignes_droite.append("")
    lignes_droite.append(f" 🔄 TOUR N° {numero_tour}")
    lignes_droite.append(f" JOUEUR ACTUEL : {joueur.nom} {joueur.emoji}")
    lignes_droite.append(" " + "-" * 30)
    
    if mode_selection:
        lignes_droite.append(" SÉLECTION DE LA PIECE")
        lignes_droite.append(" (Tapez '99' pour PASSER)")
        lignes_droite.append(f" > CHOIX : {saisie_en_cours}_") 
        lignes_droite.append(" " + "-" * 30)
        
        if message_erreur:
            lignes_droite.append(f" ⚠️  {message_erreur}")
            lignes_droite.append("")
            
        lignes_droite.extend(joueur.recuperer_lignes_inventaire())
    else:
        lignes_droite.append(" PLACEMENT")
        lignes_droite.append(" FLÈCHES : Déplacer")
        lignes_droite.append(" ESPACE  : Pivoter")
        lignes_droite.append(" ENTRÉE  : Valider")
        lignes_droite.append(" ECHAP   : Annuler choix")
        lignes_droite.append(" " + "-" * 30)
        if message_erreur:
            lignes_droite.append("")
            lignes_droite.append(f" ❌ {message_erreur}")
    
    hauteur_max = max(len(lignes_g), len(lignes_droite))
    LARGEUR_ZONE_GAUCHE = len(grille[0]) * 3 + 10 
    
    buffer_affichage = ""
    for i in range(hauteur_max):
        g_txt = lignes_g[i] if i < len(lignes_g) else ""
        d_txt = lignes_droite[i] if i < len(lignes_droite) else ""
        
        len_visu = calcul_longueur_visuelle(g_txt)
        padding_necessaire = LARGEUR_ZONE_GAUCHE - len_visu
        if padding_necessaire < 2: padding_necessaire = 2
        
        buffer_affichage += g_txt + (" " * padding_necessaire) + d_txt + "\n"
    
    print(buffer_affichage)

# =============================================================================
# 5. LOGIQUE DU JEU (RÈGLES ET CONTRÔLES)
# =============================================================================

def saisir_choix_interactif(grille, joueur, message_erreur, numero_tour):
    buffer = ""
    while True:
        afficher_interface_complete(grille, joueur, mode_selection=True, message_erreur=message_erreur, saisie_en_cours=buffer, numero_tour=numero_tour)
        
        touche = msvcrt.getch()
        
        if touche == b'\r': 
            if buffer.isdigit(): return int(buffer)
            return -1 
        elif touche == b'\x08':
            buffer = buffer[:-1]
        elif touche.isdigit():
            buffer += touche.decode('utf-8')

def verifier_placement(grille, piece, l_dep, c_dep, joueur):
    h, w = len(piece.forme), len(piece.forme[0])
    nb_l, nb_c = len(grille), len(grille[0])
    coin_ok = False; angle_ok = False
    
    for l in range(h):
        for c in range(w):
            if piece.forme[l][c] == 1:
                tl, tc = l_dep + l, c_dep + c
                if not (0 <= tl < nb_l and 0 <= tc < nb_c): return False, "Hors limites"
                if grille[tl][tc] != 0: return False, "Case occupée"
                
                if joueur.premier_tour:
                    if (tl, tc) in [(0,0), (0, nb_c-1), (nb_l-1, 0), (nb_l-1, nb_c-1)]: 
                        coin_ok = True
                else:
                    for vl, vc in [(tl-1,tc), (tl+1,tc), (tl,tc-1), (tl,tc+1)]:
                        if 0 <= vl < nb_l and 0 <= vc < nb_c and grille[vl][vc] == joueur.emoji:
                            return False, "Touche un côté de même couleur !"
                    for al, ac in [(tl-1,tc-1), (tl-1,tc+1), (tl+1,tc-1), (tl+1,tc+1)]:
                        if 0 <= al < nb_l and 0 <= ac < nb_c and grille[al][ac] == joueur.emoji:
                            angle_ok = True
                            
    if joueur.premier_tour: return (True, "OK") if coin_ok else (False, "Premier tour : Commencez dans un coin")
    else: return (True, "OK") if angle_ok else (False, "La pièce doit toucher un angle de votre couleur")

def poser_piece(grille, piece, l, c, joueur):
    for pl in range(len(piece.forme)):
        for pc in range(len(piece.forme[0])):
            if piece.forme[pl][pc] == 1: 
                grille[l + pl][c + pc] = joueur.emoji
    piece.posee = True
    joueur.premier_tour = False

def deplacer_et_poser(grille, piece, joueur, numero_tour):
    l, c = 0, 0
    msg_erreur = ""
    while True:
        afficher_interface_complete(grille, joueur, piece, l, c, mode_selection=False, message_erreur=msg_erreur, numero_tour=numero_tour)
        msg_erreur = "" 
        
        touche = msvcrt.getch()
        if touche == b'\xe0': 
            fleche = msvcrt.getch()
            if fleche == b'H' and l > -5: l -= 1
            elif fleche == b'P' and l < 20: l += 1
            elif fleche == b'K' and c > -5: c -= 1
            elif fleche == b'M' and c < 20: c += 1
        elif touche == b' ': piece.pivoter()
        elif touche == b'\x1b': return False 
        elif touche == b'\r': 
            ok, msg = verifier_placement(grille, piece, l, c, joueur)
            if ok: 
                poser_piece(grille, piece, l, c, joueur)
                return True
            else: 
                msg_erreur = msg

def calculer_score(joueur):
    """
    Calcule le score final selon les règles Blokus :
    -1 par carré (unités) non posé.
    +15 si toutes les pièces sont posées.
    """
    carres_restants = 0
    pieces_restantes = 0
    
    for p in joueur.main:
        if not p.posee:
            pieces_restantes += 1
            # On compte le nombre de '1' dans la matrice de la forme
            for row in p.forme:
                carres_restants += row.count(1)
    
    if pieces_restantes == 0:
        return 15 # Bonus si tout posé
    else:
        return -carres_restants

# =============================================================================
# 6. DONNÉES GLOBALES (PIÈCES)
# =============================================================================

PIECES_FORMES = [
    [[1]], [[1, 1]], [[1, 1], [0, 1]], [[1, 1, 1]], [[1, 1], [1, 1]],                       
    [[0, 1, 0], [1, 1, 1]], [[1, 1, 1, 1]], [[0, 0, 1], [1, 1, 1]], [[0, 1, 1], [1, 1, 0]],                 
    [[0, 1], [0, 1], [1, 1]], [[1, 0], [1, 0], [1, 0], [1, 1]], [[0, 1, 0], [0, 1, 0], [1, 1, 1]],      
    [[1, 1], [1, 0], [1, 1]], [[1, 0], [1, 1], [1, 1]], [[0, 1], [1, 1], [1, 0], [1, 0]],       
    [[0, 1, 1], [1, 1, 0], [0, 1, 0]], [[1, 1, 1, 1, 1]], [[1, 1, 0], [0, 1, 1], [0, 0, 1]],      
    [[1, 0, 0], [1, 1, 1], [0, 1, 0]], [[0, 1, 0], [1, 1, 1], [0, 1, 0]], [[0, 0, 1, 1], [1, 1, 1, 0]]            
]

# =============================================================================
# BLOC DE TEST : EXECUTION DIRECTE (F5)
# Configuration spéciale 2 JOUEURS (mais 4 Couleurs)
# =============================================================================

if __name__ == "__main__":
    # 1. On initialise la grille
    grille = init_grille(20, 20)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== BLOKUS : MODE 2 JOUEURS ==="
          "\nREGLES DU JEU :\n\n" \
    "1- MATERIEL:\nLe jeu se compose des éléments suivants:" \
    "Un plateau de jeu de 400 cases.\n" \
    "84 pièces (21 pièces dans chacune des quatre couleurs ). \n" \
    "Chacune des 21 pièces est de forme différente: \nIl y a 1 pièce d’un carré," \
    "1 pièce à deux carrés, 2 pièces à trois carrés, 5 pièces à quatre carrés, 12" \
    "pièces à cinq carré. \n\n" \
    "2- BUT DU JEU:\nPour chaque joueur, placer ses 21 pièces sur le plateau.\n\n" \
    "3- DEROULEMENT D'UNE PARTIE:\n" \
    "L’ordre dans lequel on joue est le suivant:\n" \
    "bleu, rouge, vert, jaune.\n" \
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
    "+20 points si les 21 pièces ont été posées.\n\n")
    print("Dans ce mode, chaque joueur contrôle 2 couleurs.")
    print("Ordre: Bleu -> Jaune -> Rouge -> Vert\n\n")
    
    nom1 = input("Entrez le nom du Joueur 1 (Bleu et Rouge) : ")
    nom2 = input("Entrez le nom du Joueur 2 (Jaune et Vert) : ")

    # 2. On crée 4 instances "Joueur" pour respecter les couleurs
    # Mais les noms indiquent qui joue quoi.
    joueurs = [
        # Joueur 1 joue la première couleur (BLEU)
        Joueur(f"{nom1}", "🟦", PIECES_FORMES),
        
        # Joueur 2 joue la deuxième couleur (JAUNE)
        Joueur(f"{nom2}", "🟨", PIECES_FORMES),
        
        # Joueur 1 joue la troisième couleur (ROUGE)
        Joueur(f"{nom1}", "🟥", PIECES_FORMES),
        
        # Joueur 2 joue la quatrième couleur (VERT)
        Joueur(f"{nom2}", "🟩", PIECES_FORMES)
    ]
    
    compteur_passes = 0
    jeu_termine = False
    
    # NOUVEAU : Compteur global de tours
    nb_tours_global = 1

    # 3. Boucle de jeu de test
    while not jeu_termine:
        # On itère sur les 4 "couleurs", les humains alternent donc automatiquement
        for joueur in joueurs:
            # Vérification de fin de partie AVANT le tour
            if compteur_passes >= 4:
                jeu_termine = True
                break

            choix_valide = False
            msg_err = ""
            
            while not choix_valide:
                choix = saisir_choix_interactif(grille, joueur, msg_err, nb_tours_global)
                
                # Code retour -1 ou 99 = Passer son tour
                if choix == -1 or choix == 99:
                    compteur_passes += 1
                    choix_valide = True
                    
                # Vérification de l'inventaire
                elif 0 <= choix < len(joueur.main):
                    if joueur.main[choix].posee:
                        msg_err = "Cette pièce est déjà posée !"
                    else:
                        piece = joueur.main[choix]
                        # Lancement du mode déplacement
                        if deplacer_et_poser(grille, piece, joueur, nb_tours_global):
                            compteur_passes = 0 # On a joué, on reset le compteur
                            choix_valide = True
                        else:
                            msg_err = "Placement annulé."
                else:
                    msg_err = "Numéro invalide."
        
        # Si le jeu n'est pas fini après un tour de table complet (les 4 couleurs)
        if not jeu_termine:
            nb_tours_global += 1

    # === FIN DE PARTIE ===
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*50)
    print("       🏁  FIN DE LA PARTIE (2 Joueurs)  🏁       ")
    print(f"       Nombre total de tours : {nb_tours_global-1}")
    print("="*50 + "\n")
    
    scores_finaux = {}
    
    # On additionne les scores des couleurs appartenant au même joueur
    for joueur_coul in joueurs:
        points = calculer_score(joueur_coul)
        
        # Si le nom existe déjà (ex: Josey a déjà joué Bleu), on ajoute le score de Rouge
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
        medaille = "🥇" if i == 0 else "🥈"
        print(f" {medaille} {nom} : {score} points")
        
    print("\nMerci d'avoir joué !!!\n" \
    "\nRéalisé par Célia et José")
    print("="*50)
    input("Appuyez sur Entrée pour quitter...")