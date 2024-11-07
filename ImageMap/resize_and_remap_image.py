import torch
import torch.nn.functional as F
import logging
from multilingual_support import language_manager
import gc
import numpy as np

def find_nearest_neighbor_batch(block: torch.Tensor, palette: torch.Tensor, batch_size: int = 1000) -> torch.Tensor:
    n_pixels = block.shape[0]
    n_colors = palette.shape[0]
    min_indices = torch.zeros(n_pixels, dtype=torch.long, device=block.device)
    min_distances = torch.full((n_pixels,), float('inf'), device=block.device)
    
    for i in range(0, n_pixels, batch_size):
        pixel_batch = block[i:i + batch_size]
        distances = torch.cdist(pixel_batch, palette)
        batch_min_distances, batch_indices = torch.min(distances, dim=1)
        
        min_distances[i:i + batch_size] = batch_min_distances
        min_indices[i:i + batch_size] = batch_indices
        
        if i % (batch_size * 10) == 0:
            torch.cuda.empty_cache()
    
    return min_indices

def resize_and_remap_image_impl(image: torch.Tensor, scale: float, palette: torch.Tensor, 
                              block_size: int, device: torch.device, progress_function) -> torch.Tensor:
    try:
        torch.cuda.empty_cache()
        gc.collect()
        
        if image.dim() == 3:
            image = image.unsqueeze(0)
        
        b, h, w, c = image.shape
        if h == 0 or w == 0:
            raise ValueError(f"Invalid image dimensions: {image.shape}")
            
        new_h = max(1, int(h * scale))
        new_w = max(1, int(w * scale))
        
        print(f"Original size: {h}x{w}, New size: {new_h}x{new_w}")
        
        image = image.float()
        if image.max() > 1.0:
            image = image / 255.0
            
        palette = palette.to(image.dtype).to(device)
        if palette.max() > 1.0:
            palette = palette.float() / 255.0

        remapped_image = torch.empty((b, new_h, new_w, 3), dtype=torch.uint8, device='cpu')
        
        progress_function(51)
        print(language_manager.translate('resizing_image'))
        
        strip_height = min(block_size, new_h)
        num_strips = (new_h - 1) // strip_height + 1
        
        for strip_idx in range(num_strips):
            start_h = strip_idx * strip_height
            end_h = min((strip_idx + 1) * strip_height, new_h)
            
            src_start_h = int(start_h / scale)
            src_end_h = min(h, int(np.ceil(end_h / scale)))
            
            if src_end_h <= src_start_h:
                continue
                
            strip = F.interpolate(
                image[:, src_start_h:src_end_h, :, :].permute(0, 3, 1, 2),
                size=(end_h - start_h, new_w),
                mode='bicubic',
                align_corners=False
            ).permute(0, 2, 3, 1)
            
            for x in range(0, new_w, block_size):
                block_w = min(block_size, new_w - x)
                
                block = strip[:, :, x:x+block_w, :]
                pixels = block.reshape(-1, 3)
                
                indices = find_nearest_neighbor_batch(pixels, palette)
                remapped_pixels = palette[indices]
                remapped_block = remapped_pixels.reshape(block.shape)
                
                block_uint8 = (remapped_block * 255).round().clamp(0, 255).cpu().byte()
                remapped_image[:, start_h:end_h, x:x+block_w, :] = block_uint8
                
                progress = 51 + int(49 * ((strip_idx * new_w + x) / (new_h * new_w)))
                progress_function(progress)
                if progress % 10 == 0:
                    print(language_manager.translate('remapping_progress').format(progress))
                
                torch.cuda.empty_cache()
                
        if b == 1:
            remapped_image = remapped_image.squeeze(0)
            
        return remapped_image
        
    except Exception as e:
        print(f"{language_manager.translate('error_occurred')}: {e}")
        logging.error(f"{language_manager.translate('error_occurred')}: {e}", exc_info=True)
        raise e

def resize_and_remap_image(image, scale: float, palette: torch.Tensor, block_size: int, progress_function) -> torch.Tensor:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    if device.type == 'cuda':
        torch.cuda.empty_cache()
        torch.cuda.set_per_process_memory_fraction(0.7)
    
    image_tensor = torch.as_tensor(image, device=device)
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