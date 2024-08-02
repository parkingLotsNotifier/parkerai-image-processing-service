import random
import os
from skimage.util import random_noise
from PIL import Image, ImageEnhance
import numpy as np
import cv2
from io import BytesIO
import base64

def create_random_variants(image, dest_dir='variants_output', name='image'):
    variants = []
    num_random_variants = 5

    os.makedirs(dest_dir, exist_ok=True)

    for i in range(num_random_variants):
        variant = image.copy()

        # Random brightness adjustment
        brightness_factor = random.uniform(0.5, 1.5)
        enhancer = ImageEnhance.Brightness(variant)
        variant = enhancer.enhance(brightness_factor)

        # Random contrast adjustment
        contrast_factor = random.uniform(0.5, 1.5)
        enhancer = ImageEnhance.Contrast(variant)
        variant = enhancer.enhance(contrast_factor)

        # Random color adjustment
        color_factor = random.uniform(0.5, 1.5)
        enhancer = ImageEnhance.Color(variant)
        variant = enhancer.enhance(color_factor)

        # Random grain (noise) addition
        cv_image = cv2.cvtColor(np.array(variant), cv2.COLOR_RGB2BGR)
        grain_amount = random.uniform(0.01, 0.05)
        noise_img = random_noise(cv_image, mode='gaussian', var=grain_amount)
        noise_img = np.array(255 * noise_img, dtype='uint8')

        # Convert back to PIL image
        variant_image = Image.fromarray(cv2.cvtColor(noise_img, cv2.COLOR_BGR2RGB))
        variants.append(variant_image)

        save_image(variant_image, os.path.join(dest_dir, f'{name}_variant_{i+1}.jpg'))

    # Rotation variants
    for angle in [90, 180, 270]:
        rotated_variant = image.rotate(angle)
        variants.append(rotated_variant)
        save_image(rotated_variant, os.path.join(dest_dir, f'{name}_rotate_{angle}.jpg'))

    variants_base64 = [encode_image(np.array(variant)) for variant in variants]
    return variants_base64

# Utility function to save image
def save_image(image, path):
    image.save(path)

# Utility function to encode image
def encode_image(image):
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

