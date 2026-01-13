import os
import msvcrt
import copy


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
# 1. CONFIGURATION ET CONSTANTES
# =============================================================================

VIDE_STR = " . "
LARGEUR_VISUELLE_BLOC = 3

# =============================================================================
# 2. CLASSES DU JEU
# =============================================================================

class Piece:
    def __init__(self, forme):
        self.forme = forme
        self.posee = False

    def pivoter(self):
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
# 3. MOTEUR D'AFFICHAGE
# =============================================================================

def calcul_longueur_visuelle(chaine):
    longueur = 0
    for char in chaine:
        if ord(char) > 1000: longueur += 2
        else: longueur += 1
    return longueur

def init_grille(nb_ligne, nb_colonne):
    return [[0 for _ in range(nb_colonne)] for _ in range(nb_ligne)]

def preparer_rendu_grille(grille_base, piece=None, pl=0, pc=0, joueur=None):
    nb_l = len(grille_base)
    nb_c = len(grille_base[0])
    rendu = [row[:] for row in grille_base]

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
    for j in range(nb_c): header += f"{j:^3}"
    lignes_grille.append(header)
    lignes_grille.append("   ┌" + "───" * nb_c + "┐")
    for i in range(nb_l):
        ligne_str = f"{i:2} │" 
        for j in range(nb_c):
            val = rendu[i][j]
            if val == 0: ligne_str += VIDE_STR
            elif val == -1: ligne_str += "❌ "
            elif isinstance(val, str): ligne_str += val + " " 
        ligne_str += "│"
        lignes_grille.append(ligne_str)
    lignes_grille.append("   └" + "───" * nb_c + "┘")
    return lignes_grille

# =============================================================================
# 4. GESTION DE L'INTERFACE
# =============================================================================

def afficher_interface_complete(grille, joueur, piece_active=None, l=0, c=0, mode_selection=True, message_erreur="", saisie_en_cours="", info_tour=""):
    os.system('cls' if os.name == 'nt' else 'clear')
    lignes_g = preparer_rendu_grille(grille, piece_active, l, c, joueur)
    lignes_droite = ["", f" {info_tour}", f" C'EST AU TOUR DE : {joueur.nom} {joueur.emoji}", " " + "-" * 30]
    
    if mode_selection:
        lignes_droite.append(" SÉLECTION DE LA PIECE")
        lignes_droite.append(" (Tapez '99' pour PASSER si bloqué)") 
        lignes_droite.append(f" > CHOIX : {saisie_en_cours}_") 
        lignes_droite.append(" " + "-" * 30)
        if message_erreur:
            lignes_droite.append(f" ⚠️  {message_erreur}")
            lignes_droite.append("")
        lignes_droite.extend(joueur.recuperer_lignes_inventaire())
    else:
        lignes_droite.extend([" PLACEMENT", " FLÈCHES : Déplacer", " ESPACE  : Pivoter", " ENTRÉE  : Valider", " ECHAP   : Annuler", " " + "-" * 30])
        if message_erreur: lignes_droite.append(f"\n ❌ {message_erreur}")
    
    hauteur = max(len(lignes_g), len(lignes_droite))
    LARGEUR_GAUCHE = len(grille[0]) * 3 + 10 
    
    buffer = ""
    for i in range(hauteur):
        g_txt = lignes_g[i] if i < len(lignes_g) else ""
        d_txt = lignes_droite[i] if i < len(lignes_droite) else ""
        pad = max(2, LARGEUR_GAUCHE - calcul_longueur_visuelle(g_txt))
        buffer += g_txt + (" " * pad) + d_txt + "\n"
    print(buffer)

# =============================================================================
# 5. LOGIQUE DE JEU
# =============================================================================

def saisir_choix_interactif(grille, joueur, message_erreur, info_tour=""):
    buffer = ""
    while True:
        afficher_interface_complete(grille, joueur, mode_selection=True, message_erreur=message_erreur, saisie_en_cours=buffer, info_tour=info_tour)
        touche = msvcrt.getch()
        if touche == b'\r': 
            return int(buffer) if buffer.isdigit() else -1
        elif touche == b'\x08': buffer = buffer[:-1]
        elif touche.isdigit(): buffer += touche.decode('utf-8')

def verifier_placement(grille, piece, l_dep, c_dep, joueur):
    h, w = len(piece.forme), len(piece.forme[0])
    nb_l, nb_c = len(grille), len(grille[0])
    coin_ok, angle_ok = False, False
    
    for l in range(h):
        for c in range(w):
            if piece.forme[l][c] == 1:
                tl, tc = l_dep + l, c_dep + c
                if not (0 <= tl < nb_l and 0 <= tc < nb_c): return False, "Hors limites"
                if grille[tl][tc] != 0: return False, "Case occupée"
                if joueur.premier_tour:
                    if (tl, tc) in [(0,0), (0, nb_c-1), (nb_l-1, 0), (nb_l-1, nb_c-1)]: coin_ok = True
                else:
                    for vl, vc in [(tl-1,tc), (tl+1,tc), (tl,tc-1), (tl,tc+1)]:
                        if 0 <= vl < nb_l and 0 <= vc < nb_c and grille[vl][vc] == joueur.emoji: return False, "Touche un côté !"
                    for al, ac in [(tl-1,tc-1), (tl-1,tc+1), (tl+1,tc-1), (tl+1,tc+1)]:
                        if 0 <= al < nb_l and 0 <= ac < nb_c and grille[al][ac] == joueur.emoji: angle_ok = True
                            
    if joueur.premier_tour: return (True, "OK") if coin_ok else (False, "Premier tour : Coin obligatoire")
    else: return (True, "OK") if angle_ok else (False, "Doit toucher un angle")

def poser_piece(grille, piece, l, c, joueur):
    for pl in range(len(piece.forme)):
        for pc in range(len(piece.forme[0])):
            if piece.forme[pl][pc] == 1: grille[l + pl][c + pc] = joueur.emoji
    piece.posee = True
    joueur.premier_tour = False

def deplacer_et_poser(grille, piece, joueur, info_tour=""):
    l, c, msg_err = 0, 0, ""
    while True:
        afficher_interface_complete(grille, joueur, piece, l, c, mode_selection=False, message_erreur=msg_err, info_tour=info_tour)
        msg_err = "" 
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
            else: msg_err = msg

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
# DONNÉES
# =============================================================================
PIECES_FORMES = [
    [[1]], [[1, 1]], [[1, 1], [0, 1]], [[1, 1, 1]], [[1, 1], [1, 1]],                       
    [[0, 1, 0], [1, 1, 1]], [[1, 1, 1, 1]], [[0, 0, 1], [1, 1, 1]], [[0, 1, 1], [1, 1, 0]],                 
    [[0, 1], [0, 1], [1, 1]], [[1, 0], [1, 0], [1, 0], [1, 1]], [[0, 1, 0], [0, 1, 0], [1, 1, 1]],      
    [[1, 1], [1, 0], [1, 1]], [[1, 0], [1, 1], [1, 1]], [[0, 1], [1, 1], [1, 0], [1, 0]],       
    [[0, 1, 1], [1, 1, 0], [0, 1, 0]], [[1, 1, 1, 1, 1]], [[1, 1, 0], [0, 1, 1], [0, 0, 1]],      
    [[1, 0, 0], [1, 1, 1], [0, 1, 0]], [[0, 1, 0], [1, 1, 1], [0, 1, 0]], [[0, 0, 1, 1], [1, 1, 1, 0]]            
]