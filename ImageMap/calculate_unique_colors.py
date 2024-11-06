import torch
from multilingual_support import language_manager

def calculate_unique_colors(image_tensor):
    if image_tensor is None or image_tensor.numel() == 0:
        raise ValueError("The image is empty.")

    pixels = image_tensor.view(-1, image_tensor.shape[-1])
    unique_colors = torch.unique(pixels, dim=0)
    number_of_unique_colors = unique_colors.size(0)
    print(language_manager.translate("unique_colors"), number_of_unique_colors)
    return number_of_unique_colors