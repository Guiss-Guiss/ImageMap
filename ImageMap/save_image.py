import cv2
import numpy as np
import torch
import logging
from multilingual_support import language_manager

def save_image(image, output_path):
    try:
        save_image_to_path(image, output_path)
        logging.info(language_manager.translate('image_saved'))
        print(language_manager.translate('image_saved'))
    except Exception as e:
        logging.error(f"Failed to save image: {e}", exc_info=True)
        print(f"Failed to save image: {e}")

def save_image_to_path(image, output_path):
    if isinstance(image, torch.Tensor):
        image = image.cpu().numpy()

    if not isinstance(image, np.ndarray):
        raise TypeError("Image must be a numpy array or a torch tensor")

    if image.dtype != np.uint8:
        image = (image * 255).astype(np.uint8)

    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    cv2.imwrite(output_path, image)