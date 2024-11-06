import torch

def verifier_cuda():
    if torch.cuda.is_available():
        print("CUDA est disponible.")
        print(f"Nombre de GPU : {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i} : {torch.cuda.get_device_name(i)}")
            print(f"CUDA Capable : {torch.cuda.is_available()}")
            print(f"Mémoire totale : {torch.cuda.get_device_properties(i).total_memory / (1024 ** 2)} MiB")
            print(f"Mémoire allouée : {torch.cuda.memory_allocated(i)} octets")
            print(f"Mémoire réservée : {torch.cuda.memory_reserved(i)} octets")
            print("----------------------------------------------------")
    else:
        print("CUDA n'est pas disponible.")

verifier_cuda()
