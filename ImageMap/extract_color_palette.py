import torch
import numpy as np
import subprocess
from sklearn.cluster import MiniBatchKMeans
from multilingual_support import language_manager
import logging

def extract_color_palette(image, number_of_colors, progress_function, number_iterations=25, batch_size=10000):

    print(language_manager.translate("color_palette_processing"))
    
    if image is None or (isinstance(image, np.ndarray) and image.size == 0) or (isinstance(image, torch.Tensor) and image.numel() == 0):
        raise ValueError("extract_color_palette: the image is empty")

    progress_function(0)

    if isinstance(image, torch.Tensor):
        image = image.cpu().numpy()

    if image.max() > 1.0:
        image = image.astype(np.float32) / 255.0

    pixels = image.reshape(-1, 3)
    number_pixels = pixels.shape[0]

    if number_of_colors > number_pixels:
        number_of_colors = number_pixels

    kmeans = MiniBatchKMeans(n_clusters=number_of_colors,
                             n_init=10,
                             batch_size=min(batch_size, number_pixels),
                             max_iter=number_iterations,
                             verbose=0)

    total_iterations = (number_pixels // batch_size) + 1
    for i in range(0, number_pixels, batch_size):
        batch = pixels[i:min(i+batch_size, number_pixels)]
        kmeans.partial_fit(batch)
        progress = int(100 * (i / number_pixels))
        progress_function(progress)

    centers = kmeans.cluster_centers_
    brightness = np.mean(centers, axis=1)
    sorted_indices = np.argsort(brightness)
    sorted_centers = centers[sorted_indices]

    palette = sorted_centers.tolist()

    progress_function(100)

    logging.info(language_manager.translate("color_palette_done"))
    print(language_manager.translate("color_palette_done"))

    return palette

def adjust_chunk_size_via_nvidia_smi(gpu_id, number_of_colors, minimum_size=5000, maximum_size=100000):
    free_memory = get_gpu_memory_via_nvidia_smi()
    if free_memory and len(free_memory) > gpu_id:
        free_memory_gpu = free_memory[gpu_id] * 1024 * 1024  # Convert MiB to bytes

        estimated_memory_per_pixel = 3 * 4  # 3 channels (RGB) * 4 bytes (float32)
        chunk_size = int(free_memory_gpu // (number_of_colors * estimated_memory_per_pixel))

        chunk_size = max(min(chunk_size, maximum_size), minimum_size)
        return chunk_size
    else:
        return minimum_size

def detect_system_configuration():
    if torch.cuda.is_available():
        number_of_gpus = torch.cuda.device_count()
        return number_of_gpus
    else:
        return 0

def get_gpu_memory_via_nvidia_smi():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader'], stdout=subprocess.PIPE)
        free_memory = [int(x) for x in result.stdout.decode('utf-8').splitlines()]
        return free_memory
    except Exception as e:
        logging.error(f"Error retrieving GPU memory via nvidia-smi: {e}", exc_info=True)
        return None