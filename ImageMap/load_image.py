import cv2
import torch
import logging
from multilingual_support import LanguageManager

language_manager = LanguageManager()

def load_image(image_path):
    try:
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            logging.error("Failed to load image. Image is None.")
            return None

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_tensor = torch.from_numpy(image_rgb).to(device).float() / 255.0

        logging.info(language_manager.translate("image_loaded_successfully"))
        print(language_manager.translate("image_loaded_successfully"))
        return image_tensor
    except Exception as e:
        logging.error(f"Error loading image: {e}", exc_info=True)
        raise e