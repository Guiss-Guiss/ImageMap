import subprocess

def afficher_statut_gpu():
    try:
        resultat = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE)
        print(resultat.stdout.decode('utf-8'))
    except Exception as e:
        print(f"Erreur lors de l'exécution de nvidia-smi : {e}")


afficher_statut_gpu()

import torch

def surveiller_memoires():
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: mémoire allouée : {torch.cuda.memory_allocated(i)} octets")
        print(f"GPU {i}: mémoire réservée : {torch.cuda.memory_reserved(i)} octets")
        print(f"GPU {i}: mémoire libre estimée (réservée - allouée) : {torch.cuda.memory_reserved(i) - torch.cuda.memory_allocated(i)} octets")
        print("----------------------------------------------------")

surveiller_memoires()

def main():
    afficher_statut_gpu()
    surveiller_memoires()

if __name__ == "__main__":
    main()





