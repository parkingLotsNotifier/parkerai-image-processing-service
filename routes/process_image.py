from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import decode_image, decode_image_from_path, handle_cropping, handle_rotation, calculate_average_intensity
from utils.variant_utils import create_random_variants
from utils.blueprint_utils import load_blueprint
from utils.firebase_logger import log_message
from PIL import Image
from io import BytesIO
import os

api = Namespace('process_image', description='Process image operations')

process_image_model = api.model('ProcessImageModel', {
    'image': fields.String(required=True, description='Base64 encoded image'),
    'actions': fields.List(fields.String, required=True, description='Actions to perform on the image'),
    'angle': fields.Integer(description='Angle to rotate the image')
})

@api.route('/process')
class ProcessImage(Resource):
    @api.expect(process_image_model)
    def post(self):
        data = request.get_json()
        image_base64 = data.get('image')
        actions = data.get('actions')
        angle = data.get('angle', 0)

        if not image_base64:
            return jsonify({'error': 'Image data must be provided'}), 400

        img = decode_image(image_base64)
        pil_img = Image.fromarray(img)
        response_data = {'message': 'Image processed successfully'}

        if 'rotate' in actions:
            rotated_image = handle_rotation(img, angle)
            response_data['rotated_image'] = {
                'name': 'rotated_image.jpg',
                'image': encode_image(rotated_image)
            }

        if 'crop' in actions:
            blueprint = load_blueprint()
            cropped_images = handle_cropping(img, blueprint)
            response_data['cropped_images'] = [
                {'name': f'cropped_image_{i+1}.jpg', 'image': encode_image(cropped_image)}
                for i, cropped_image in enumerate(cropped_images)
            ]

        if 'create_variants' in actions:
            variants = create_random_variants(pil_img)
            response_data['variants'] = [
                {'name': f'variant_{i+1}.jpg', 'image': encode_image(variant)}
                for i, variant in enumerate(variants)
            ]

        log_message("Processed image successfully", "INFO")
        return jsonify(response_data)
