from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import decode_image_from_base64, calculate_average_intensity
from utils.firebase_logger import log_message

api = Namespace('average_intensity', description='Calculate average intensity operations')

average_intensity_model = api.model('AverageIntensityModel', {
    'image': fields.String(required=True, description='Base64 encoded image')
})

@api.route('/',strict_slashes=False)
class AverageIntensity(Resource):
    @api.expect(average_intensity_model)
    def post(self):
        data = request.get_json()
        image_base64 = data.get('image')

        if not image_base64:
            return jsonify({'error': 'Image data must be provided'}), 400

        # Decode base64 to numpy array
        img = decode_image_from_base64(image_base64)
        
        # Calculate average intensity
        average_intensity = calculate_average_intensity(img)

        log_message("Calculated average intensity successfully", "INFO")
        return jsonify({
            'average_intensity': average_intensity
        })
