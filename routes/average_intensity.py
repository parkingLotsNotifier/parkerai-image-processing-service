from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import decode_image, decode_image_from_path, calculate_average_intensity
from utils.firebase_logger import log_message
import os

api = Namespace('average_intensity', description='Calculate average intensity operations')

average_intensity_model = api.model('AverageIntensityModel', {
    'image': fields.String(required=True, description='Base64 encoded image')
})

@api.route('/')
class AverageIntensity(Resource):
    @api.expect(average_intensity_model)
    def post(self):
        data = request.get_json()
        image_base64 = data.get('image')

        if not image_base64:
            return jsonify({'error': 'Image data must be provided'}), 400

        img = decode_image(image_base64)
        average_intensity = calculate_average_intensity(img)

        log_message("Calculated average intensity successfully", "INFO")
        return jsonify({
            'message': 'Average intensity calculated successfully',
            'average_intensity': average_intensity
        })
