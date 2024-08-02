from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.variant_utils import create_random_variants
from utils.firebase_logger import log_message
from PIL import Image
from io import BytesIO
import os
import base64

api = Namespace('create_variants', description='Create image variants operations')

create_variants_model = api.model('CreateVariantsModel', {
    'image': fields.String(required=True, description='Base64 encoded image')
})

@api.route('/')
class CreateVariants(Resource):
    @api.expect(create_variants_model)
    def post(self):
        data = request.get_json()
        image_base64 = data.get('image')

        if not image_base64:
            return jsonify({'error': 'Image data must be provided'}), 400

        img = decode_image(image_base64)
        pil_img = Image.fromarray(img)
        variants = create_random_variants(pil_img)

        variants_response = [
            {'name': f'variant_{i+1}.jpg', 'image': encode_image(variant)}
            for i, variant in enumerate(variants)
        ]

        log_message("Created image variants successfully", "INFO")
        return jsonify({
            'message': 'Image variants created successfully',
            'variants': variants_response
        })
