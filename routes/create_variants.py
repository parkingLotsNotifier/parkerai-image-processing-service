from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import decode_image_from_base64, encode_image_to_base64
from utils.variant_utils import create_random_variants
from utils.firebase_logger import log_message

api = Namespace('create_variants', description='Create image variants operations')

create_variants_model = api.model('CreateVariantsModel', {
    'image': fields.String(required=True, description='Base64 encoded image')
})

@api.route('/', strict_slashes=False)
class CreateVariants(Resource):
    @api.expect(create_variants_model)
    def post(self):
        data = request.get_json()
        image_base64 = data.get('image')

        if not image_base64:
            return jsonify({'error': 'Image data must be provided'}), 400

        # Decode base64 to numpy array
        img = decode_image_from_base64(image_base64)
        
        # Create variants
        variants = create_random_variants(img)
        variants_response = [
            {'name': f'variant_{i+1}.jpg', 'image': encode_image_to_base64(variant)}
            for i, variant in enumerate(variants)
        ]

        log_message("Created image variants successfully", "INFO")
        return jsonify({
            'variants': variants_response
        })
