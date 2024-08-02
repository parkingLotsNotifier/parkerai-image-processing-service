import cv2
import numpy as np
import base64
from datetime import datetime
from PIL import Image
import os

# Image encoding and decoding functions
def decode_image(image_base64):
    image = base64.b64decode(image_base64)
    np_arr = np.frombuffer(image, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def decode_image_from_path(image_path):
    img = cv2.imread(image_path)
    return img

def encode_image(image):
    _, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

# Image saving function
def save_image(image, path):
    image.save(path)

# Generate filenames based on a pattern
def generate_filename(name):
    now = datetime.now()
    timestamp = now.strftime("%d.%m.%Y-%H:%M:%S")
    filename = f"picture-[Prototype]-{timestamp}_{name}.jpg"
    return filename

# Cropping function
def handle_cropping(img, blueprint, dest_dir, image_name):
    annotations = blueprint['annotations']
    categories = {category['id']: category['name'] for category in blueprint['categories']}
    cropped_images = []

    for annotation in annotations:
        x, y, w, h = annotation['bbox']
        cropped_img = img[int(y):int(y+h), int(x):int(x+w)]
        name = categories[annotation['category_id']]
        cropped_image_info = {'name': name, 'image': cropped_img}
        cropped_images.append(cropped_image_info)
        filename = generate_filename(f"{image_name}_{name}")
        cropped_pil_img = Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))
        save_image(cropped_pil_img, os.path.join(dest_dir, filename))

    return cropped_images

# Rotation function
def handle_rotation(img, angle, dest_dir):
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h))
    rotated_image_info = {'rotated_image': encode_image(rotated)}

    save_image(Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)), os.path.join(dest_dir, 'rotated_image.jpg'))

    return rotated_image_info

# Average intensity function
def calculate_average_intensity(img):
    return np.mean(img)

