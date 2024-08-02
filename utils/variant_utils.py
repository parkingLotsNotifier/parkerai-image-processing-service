import random
import numpy as np
import cv2
from skimage.util import random_noise

def create_random_variants(image):
    variants = []
    num_random_variants = 5

    for i in range(num_random_variants):
        variant = image.copy()

        # Random brightness adjustment
        brightness_factor = random.uniform(0.5, 1.5)
        variant = cv2.convertScaleAbs(variant, alpha=brightness_factor, beta=0)

        # Random contrast adjustment
        contrast_factor = random.uniform(0.5, 1.5)
        variant = cv2.convertScaleAbs(variant, alpha=contrast_factor, beta=0)

        # Random color adjustment
        hsv = cv2.cvtColor(variant, cv2.COLOR_BGR2HSV)
        hue_factor = random.uniform(0.5, 1.5)
        hsv[..., 0] = hsv[..., 0] * hue_factor
        variant = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Random grain (noise) addition
        grain_amount = random.uniform(0.01, 0.05)
        noise_img = random_noise(variant, mode='gaussian', var=grain_amount)
        variant = np.array(255 * noise_img, dtype='uint8')

        variants.append(variant)

    # Rotation variants
    for angle in [90, 180, 270]:
        rotated_variant = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE if angle == 90 else
                                             cv2.ROTATE_180 if angle == 180 else
                                             cv2.ROTATE_90_COUNTERCLOCKWISE)
        variants.append(rotated_variant)

    return variants
