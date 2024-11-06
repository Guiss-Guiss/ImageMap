import torch
import torch.nn.functional as F
import logging
from multilingual_support import language_manager

def find_nearest_neighbor_batch(block: torch.Tensor, palette: torch.Tensor, batch_size_palette: int = 1000) -> torch.Tensor:
    n_pixels = block.shape[0]
    n_colors = palette.shape[0]
    min_indices = torch.zeros(n_pixels, dtype=torch.long, device=block.device)
    min_distances = torch.full((n_pixels,), float('inf'), device=block.device)

    for i in range(0, n_colors, batch_size_palette):
        batch_palette = palette[i:i+batch_size_palette]
        distances = torch.sum((block[:, None, :] - batch_palette[None, :, :]) ** 2, dim=2)
        batch_min_distances, batch_indices = torch.min(distances, dim=1)
        mask = batch_min_distances < min_distances
        min_distances[mask] = batch_min_distances[mask]
        min_indices[mask] = batch_indices[mask] + i

    return min_indices

def resize_and_remap_image_impl(image: torch.Tensor, scale: float, palette: torch.Tensor, block_size: int, device: torch.device, progress_function) -> torch.Tensor:
    image = image.float()
    print(language_manager.translate('image_processing'))
    if image.max() > 1.0:
        image = image / 255.0

    if palette.max() > 1.0:
        palette = palette.float() / 255.0

    palette = palette.to(image.dtype).to(device)

    if palette.min() < 0 or palette.max() > 1:
        raise ValueError("Palette contains values outside the range [0, 1].")

    if torch.all(palette < 1e-6):
        raise ValueError("Extracted palette is almost entirely black. Check palette extraction.")

    if image.dim() == 3:
        image = image.unsqueeze(0)

    b, h, w, c = image.shape
    new_h, new_w = int(h * scale), int(w * scale)

    remapped_image = torch.empty((b, new_h, new_w, 3), dtype=torch.uint8, device=device)

    resized_image = F.interpolate(image.permute(0, 3, 1, 2),
                                  size=(new_h, new_w),
                                  mode='bicubic',
                                  align_corners=False).permute(0, 2, 3, 1)

    logging.info(language_manager.translate('image_processing'))

    total_blocks = ((new_h - 1) // block_size + 1) * ((new_w - 1) // block_size + 1)
    current_block = 0

    try:
        for y in range(0, new_h, block_size):
            for x in range(0, new_w, block_size):
                block_h = min(block_size, new_h - y)
                block_w = min(block_size, new_w - x)

                block = resized_image[:, y:y+block_h, x:x+block_w, :]
                flattened_block = block.reshape(-1, 3)

                indices = find_nearest_neighbor_batch(flattened_block, palette)

                remapped_block = palette[indices].reshape(block.shape)

                block_uint8 = (remapped_block * 255).round().clamp(0, 255).byte()
                remapped_image[:, y:y+block_h, x:x+block_w, :] = block_uint8

                current_block += 1
                progress = int(100 * (current_block / total_blocks))
                progress_function(progress)

        if b == 1:
            remapped_image = remapped_image.squeeze(0)

        return remapped_image.cpu()
    except Exception as e:
        print(f"Error during image resize and remap: {e}")
        logging.error(f"Error during image resize and remap: {e}", exc_info=True)
        raise e

def resize_and_remap_image(image, scale: float, palette: torch.Tensor, block_size: int, progress_function) -> torch.Tensor:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    image_tensor = torch.as_tensor(image, device=device)
    print(language_manager.translate('image_scaled'))
    logging.info(language_manager.translate('image_scaled'))

    try:
        result = resize_and_remap_image_impl(image_tensor, scale, palette, block_size, device, progress_function)
        print(language_manager.translate('image_ready'))
        logging.info(language_manager.translate('image_ready'))
        return result
    except Exception as e:
        print(f"Error during image resize and remap: {e}")
        logging.error(f"Error during image resize and remap: {e}", exc_info=True)
        raise e
