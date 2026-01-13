import asyncio
import pickle
import sys
import os

try: import blokus_multi as bk
except ImportError: sys.exit("Erreur : 'blokus_multi.py' manquant.")

HOST, PORT = '127.0.0.1', 8888

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== CLIENT J3 (En attente) ===")
    
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(">> Connecté au serveur. Attente du tour...")
    except: return

    while True:
        try:
            data = await reader.read(100000)
            if not data: break
            
            # Réception avec tour
            grille, mon_joueur, info_txt, numero_tour = pickle.loads(data)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"--- C'EST A TOI DE JOUER : {mon_joueur.nom} ---")
            
            choix_ok = False
            msg = "A toi !"
            while not choix_ok:
                choix = bk.saisir_choix_interactif(grille, mon_joueur, msg, info_txt, numero_tour=numero_tour)
                if choix == -1 or choix == 99: choix_ok = True
                elif 0 <= choix < len(mon_joueur.main) and not mon_joueur.main[choix].posee:
                    if bk.deplacer_et_poser(grille, mon_joueur.main[choix], mon_joueur, info_txt, numero_tour=numero_tour): choix_ok = True
                    else: msg = "Placement invalide !"
                else: msg = "Pièce invalide !"

            writer.write(pickle.dumps((grille, mon_joueur)))
            await writer.drain()
            print("En attente...")

        except Exception as e: break

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())