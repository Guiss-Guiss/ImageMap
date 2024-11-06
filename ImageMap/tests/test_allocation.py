import torch

def test_allocation_gpu():
    try:
        x = torch.rand((1000, 1000), device='cuda:0')
        print(f"Tenseur alloué sur GPU 0 : {x.device}")
        y = torch.rand((1000, 1000), device='cuda:1')
        print(f"Tenseur alloué sur GPU 1 : {y.device}")
    except Exception as e:
        print(f"Erreur d'allocation : {e}")

test_allocation_gpu()
