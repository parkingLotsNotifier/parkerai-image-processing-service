from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import decode_image_from_base64, handle_cropping, encode_image_to_base64
from utils.blueprint_utils import load_blueprint
from utils.firebase_logger import log_message
import numpy as np

api = Namespace('crop', description='Crop image operations')

crop_model = api.model('CropModel', {
    'image': fields.String(required=True, description='Base64 encoded image')
})

@api.route('/',strict_slashes=False)
class CropImage(Resource):
    @api.expect(crop_model)
    def post(self):
        data = request.get_json()
        image_base64 = data.get('image')

        if not image_base64:
            return jsonify({'error': 'Image data must be provided'}), 400

        try:
            # Decode base64 to numpy array
            img = decode_image_from_base64(image_base64)

            blueprint = load_blueprint()
            cropped_images = handle_cropping(img, blueprint)
            cropped_images_response = [
                {'name': f'cropped_image_{i+1}.jpg', 'image': encode_image_to_base64(cropped_image)}
                for i, cropped_image in enumerate(cropped_images)
            ]

            log_message("Cropped image successfully", "INFO")
            return jsonify({
                'cropped_images': cropped_images_response
            })
        except Exception as e:
            log_message(f"Error processing image: {e}", "ERROR")
            return jsonify({'error': str(e)}), 500
