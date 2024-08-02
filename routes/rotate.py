from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import decode_image, decode_image_from_path, handle_rotation
from utils.firebase_logger import log_message
import os

api = Namespace('rotate', description='Rotate image operations')

rotate_model = api.model('RotateModel', {
    'image': fields.String(required=True, description='Base64 encoded image'),
    'angle': fields.Integer(required=True, description='Angle to rotate the image')
})

@api.route('/')
class RotateImage(Resource):
    @api.expect(rotate_model)
    def post(self):
        data = request.get_json()
        image_base64 = data.get('image')
        angle = data.get('angle')

        if not image_base64:
            return jsonify({'error': 'Image data must be provided'}), 400

        img = decode_image(image_base64)
        rotated_image = handle_rotation(img, angle)

        log_message("Rotated image successfully", "INFO")
        return jsonify({
            'message': 'Image rotated successfully',
            'rotated_image': {
                'name': 'rotated_image.jpg',
                'image': encode_image(rotated_image)
            }
        })
