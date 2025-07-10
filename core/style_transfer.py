import torch
from torchvision import models, transforms
from core.utils import load_and_prepare, tensor_to_image
import matplotlib.pyplot as plt
import os

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

vgg19 = models.vgg19(pretrained=True).features.to(DEVICE).eval()
for p in vgg19.parameters():
    p.requires_grad = False

def extract_features(img, net):
    selected = {
        '0': 'conv1_1', '5': 'conv2_1',
        '10': 'conv3_1', '19': 'conv4_1',
        '21': 'content', '28': 'conv5_1'
    }
    features = {}
    for name, layer in net._modules.items():
        img = layer(img)
        if name in selected:
            features[selected[name]] = img
    return features

def get_gram_matrix(feature_map):
    _, d, h, w = feature_map.size()
    reshaped = feature_map.view(d, h * w)
    return torch.mm(reshaped, reshaped.t())

def apply_style(content_path, style_path, save_dir='outputs', steps=500, notify_step=500):
    os.makedirs(save_dir, exist_ok=True)

    pipeline = transforms.Compose([
        transforms.Resize(300),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
    ])

    content_img = load_and_prepare(content_path, pipeline, DEVICE)
    style_img = load_and_prepare(style_path, pipeline, DEVICE)
    generated = content_img.clone().requires_grad_(True)

    weights = {
        'conv1_1': 1.0, 'conv2_1': 0.75,
        'conv3_1': 0.5, 'conv4_1': 0.2,
        'conv5_1': 0.1
    }

    alpha = 1e2
    beta = 1e8

    content_features = extract_features(content_img, vgg19)
    style_features = extract_features(style_img, vgg19)
    style_grams = {k: get_gram_matrix(v) for k, v in style_features.items()}

    optimizer = torch.optim.Adam([generated], lr=0.006)

    for step in range(1, steps + 1):
        gen_features = extract_features(generated, vgg19)

        content_loss = torch.mean((gen_features['content'] - content_features['content']) ** 2)

        style_loss = 0
        for layer in weights:
            gen_gram = get_gram_matrix(gen_features[layer])
            style_gram = style_grams[layer]
            _, c, h, w = gen_features[layer].shape
            style_loss += weights[layer] * torch.mean((gen_gram - style_gram) ** 2) / (c * h * w)

        total_loss = alpha * content_loss + beta * style_loss

        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()

        if step % notify_step == 0 or step == steps:
            result_img = tensor_to_image(generated)
            result_path = os.path.join(save_dir, f"output_{step}.png")
            plt.imsave(result_path, result_img)
            print(f"[INFO] Step {step}/{steps} - Loss: {total_loss:.4f}")
    return result_path
