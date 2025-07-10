from PIL import Image
import numpy as np
import torch

def tensor_to_image(tensor):
    img = tensor.cpu().clone().detach().numpy().squeeze()
    img = img.transpose(1, 2, 0)
    img = img * 0.5 + 0.5  # Unnormalize
    return np.clip(img, 0, 1)

def load_and_prepare(path, transform, device):
    img = Image.open(path).convert("RGB")
    img = transform(img).unsqueeze(0).to(device)
    return img
