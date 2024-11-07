import torch
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from multilingual_support import language_manager
import logging
from typing import Optional

def get_available_devices():
    if not torch.cuda.is_available():
        return {"cpu": True, "gpu_count": 0}
    
    gpu_count = torch.cuda.device_count()
    return {"cpu": True, "gpu_count": gpu_count}

def get_safe_gpu_memory(device_id: int, safety_factor: float = 0.7) -> int:
    torch.cuda.set_device(device_id)
    total_mem = torch.cuda.get_device_properties(device_id).total_memory
    reserved_mem = torch.cuda.memory_reserved(device_id)
    allocated_mem = torch.cuda.memory_allocated(device_id)
    free_mem = total_mem - reserved_mem - allocated_mem
    return int(free_mem * safety_factor)

class CPUKMeans:
    def __init__(self, n_clusters: int):
        self.n_clusters = n_clusters
        self.kmeans = MiniBatchKMeans(
            n_clusters=n_clusters,
            batch_size=1024,
            n_init=3,
            max_iter=100,
            compute_labels=False
        )

    def fit(self, pixels: np.ndarray, progress_function) -> np.ndarray:
        n_samples = len(pixels)
        batch_size = 1024
        
        for i in range(0, n_samples, batch_size):
            end_idx = min(i + batch_size, n_samples)
            batch = pixels[i:end_idx]
            self.kmeans.partial_fit(batch)
            
            progress = int(90 * (i / n_samples))
            progress_function(progress)
            
        return self.kmeans.cluster_centers_

class GPUKMeans:
    def __init__(self, n_clusters: int, device_id: int):
        self.n_clusters = n_clusters
        self.device = f'cuda:{device_id}'
        self.device_id = device_id
        self.centroids = None
        torch.cuda.set_device(device_id)

    @torch.amp.autocast(device_type='cuda')
    def _calculate_distances(self, batch: torch.Tensor, chunk_size: Optional[int] = None) -> torch.Tensor:
        if chunk_size is None:
            available_mem = get_safe_gpu_memory(self.device_id)
            elem_size = 4
            chunk_size = available_mem // (self.n_clusters * elem_size * 3)
            chunk_size = min(chunk_size, batch.shape[0])

        if batch.shape[0] > chunk_size:
            distances = torch.zeros((batch.shape[0], self.n_clusters), device=self.device)
            for i in range(0, batch.shape[0], chunk_size):
                end_idx = min(i + chunk_size, batch.shape[0])
                chunk = batch[i:end_idx]
                
                chunk_norm = torch.sum(chunk**2, dim=1, keepdim=True)
                centroid_norm = torch.sum(self.centroids**2, dim=1, keepdim=True)
                dot_product = torch.mm(chunk, self.centroids.T)
                distances[i:end_idx] = chunk_norm + centroid_norm.T - 2 * dot_product
                
                del chunk_norm, centroid_norm, dot_product
                torch.cuda.empty_cache()
            
            return distances
        else:
            chunk_norm = torch.sum(batch**2, dim=1, keepdim=True)
            centroid_norm = torch.sum(self.centroids**2, dim=1, keepdim=True)
            dot_product = torch.mm(batch, self.centroids.T)
            return chunk_norm + centroid_norm.T - 2 * dot_product

    def fit(self, pixels: np.ndarray, progress_function) -> np.ndarray:
        n_samples = len(pixels)
        safe_mem = get_safe_gpu_memory(self.device_id)
        batch_size = min(8192, safe_mem // (pixels.shape[1] * 4 * 3))
        
        if self.centroids is None:
            idx = np.random.choice(n_samples, self.n_clusters, replace=False)
            self.centroids = torch.tensor(pixels[idx], device=self.device, dtype=torch.float32)

        for iteration in range(10):
            new_centroids = torch.zeros_like(self.centroids)
            counts = torch.zeros(self.n_clusters, device=self.device)
            
            for start_idx in range(0, n_samples, batch_size):
                end_idx = min(start_idx + batch_size, n_samples)
                batch = torch.tensor(pixels[start_idx:end_idx], device=self.device, dtype=torch.float32)
                
                distances = self._calculate_distances(batch)
                assignments = torch.argmin(distances, dim=1)
                
                for k in range(self.n_clusters):
                    mask = assignments == k
                    if mask.any():
                        new_centroids[k] += batch[mask].sum(dim=0)
                        counts[k] += mask.sum()
                
                del batch, distances, assignments
                torch.cuda.empty_cache()
                
                progress = int(90 * (start_idx / n_samples))
                progress_function(progress)

            mask = counts > 0
            new_centroids[mask] /= counts[mask, None]
            
            alpha = 0.8
            self.centroids.mul_(1 - alpha).add_(new_centroids, alpha=alpha)
            
            del new_centroids, counts, mask
            torch.cuda.empty_cache()

        result = self.centroids.cpu().numpy()
        del self.centroids
        torch.cuda.empty_cache()
        return result

def extract_color_palette(image, number_of_colors, progress_function, number_iterations=10):
    print(language_manager.translate("color_palette_processing"))
    progress_function(0)

    if isinstance(image, torch.Tensor):
        pixels = image.cpu().numpy()
    else:
        pixels = image.copy()

    if pixels.max() > 1.0:
        pixels = pixels.astype(np.float32) / 255.0
        
    pixels = pixels.reshape(-1, 3)
    
    devices = get_available_devices()
    logging.info(f"Available devices: CPU and {devices['gpu_count']} GPU(s)")
    

    if devices['gpu_count'] > 0:
        max_pixels = 200000 if devices['gpu_count'] > 1 else 150000
    else:
        max_pixels = 100000
        
    if pixels.shape[0] > max_pixels:
        indices = np.random.choice(pixels.shape[0], max_pixels, replace=False)
        pixels = pixels[indices]

    if devices['gpu_count'] == 0:
        logging.info("Using CPU for processing")
        kmeans = CPUKMeans(number_of_colors)
        centers = kmeans.fit(pixels, progress_function)
        
    elif devices['gpu_count'] == 1:
        logging.info("Using single GPU for processing")
        torch.cuda.empty_cache()
        kmeans = GPUKMeans(number_of_colors, device_id=0)
        centers = kmeans.fit(pixels, progress_function)
        
    else:
        logging.info("Using multiple GPUs for processing")
        torch.cuda.empty_cache()
        
        split_idx = len(pixels) // 2
        pixels_gpu0 = pixels[:split_idx]
        pixels_gpu1 = pixels[split_idx:]
        
        n_colors_gpu0 = number_of_colors // 2
        n_colors_gpu1 = number_of_colors - n_colors_gpu0
        
        kmeans_gpu0 = GPUKMeans(n_colors_gpu0, device_id=0)
        kmeans_gpu1 = GPUKMeans(n_colors_gpu1, device_id=1)
        
        centers_gpu0 = kmeans_gpu0.fit(pixels_gpu0, lambda p: progress_function(p // 2))
        centers_gpu1 = kmeans_gpu1.fit(pixels_gpu1, lambda p: progress_function(50 + p // 2))
        
        centers = np.vstack([centers_gpu0, centers_gpu1])
        
        final_kmeans = GPUKMeans(number_of_colors, device_id=0)
        centers = final_kmeans.fit(centers, lambda p: progress_function(90 + p // 10))


    brightness = np.mean(centers, axis=1)
    sorted_indices = np.argsort(brightness)
    sorted_centers = centers[sorted_indices]

    progress_function(100)
    print(language_manager.translate("color_palette_done"))
    
    return sorted_centers.tolist()