import cv2
import numpy as np
import base64


# Image encoding and decoding functions
def encode_image_to_base64(image):
    if not isinstance(image, np.ndarray):
        raise ValueError("The image to encode must be a numpy array.")

    _, buffer = cv2.imencode(".jpg", image)
    jpg_as_text = base64.b64encode(buffer).decode("utf-8")
    return jpg_as_text


def decode_image_from_base64(image_base64):
    image = base64.b64decode(image_base64)
    np_arr = np.frombuffer(image, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img


def handle_cropping(img, blueprint):
    annotations = blueprint["annotations"]
    categories = {
        category["id"]: category["name"] for category in blueprint["categories"]
    }
    cropped_images = []

    for annotation in annotations:
        x, y, w, h = annotation["bbox"]
        cropped_img = img[int(y) : int(y + h), int(x) : int(x + w)]
        name = categories[annotation["category_id"]]
        cropped_images.append(cropped_img)

    return cropped_images


def handle_rotation(img, angle):
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h))
    return rotated


def calculate_average_intensity(img):
    return np.mean(img)
