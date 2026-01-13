import asyncio
import pickle
import sys
import os

try: import blokus_multi as bk
except ImportError: sys.exit("Erreur : 'blokus_multi.py' manquant.")

HOST, PORT = '127.0.0.1', 8888

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== CLIENT J2 (En attente) ===")
    
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(">> Connecté au serveur. Attente du tour...")
    except:
        print("Serveur introuvable.")
        return

    while True:
        try:
            # 1. Attente des données du serveur
            data = await reader.read(100000)
            if not data: break
            
            # 2. Réception : (Grille, Mon_Joueur, Info_Tour, NUMERO_TOUR)
            grille, mon_joueur, info_txt, numero_tour = pickle.loads(data)
            
            # 3. Phase de jeu interactif
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"--- C'EST A TOI DE JOUER : {mon_joueur.nom} ---")
            if info_txt: print(info_txt)
            
            choix_ok = False
            msg = "A toi !"
            
            while not choix_ok:
                # Ajout de numero_tour
                choix = bk.saisir_choix_interactif(grille, mon_joueur, msg, info_txt, numero_tour=numero_tour)
                
                if choix == -1 or choix == 99:
                    print("Tour passé.")
                    choix_ok = True
                elif 0 <= choix < len(mon_joueur.main) and not mon_joueur.main[choix].posee:
                    piece = mon_joueur.main[choix]
                    # Ajout de numero_tour
                    if bk.deplacer_et_poser(grille, piece, mon_joueur, info_txt, numero_tour=numero_tour):
                        choix_ok = True
                    else: msg = "Placement invalide !"
                else: msg = "Pièce invalide !"

            # 4. Renvoi des données mises à jour
            print("Envoi du coup...")
            writer.write(pickle.dumps((grille, mon_joueur)))
            await writer.drain()
            print("En attente des autres joueurs...")

        except Exception as e:
            print(f"Erreur : {e}")
            break

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())