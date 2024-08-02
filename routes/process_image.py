from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import (
    decode_image_from_base64,
    handle_cropping,
    handle_rotation,
    encode_image_to_base64,
)
from utils.variant_utils import create_random_variants
from utils.blueprint_utils import load_blueprint
from utils.firebase_logger import log_message

api = Namespace("process_image", description="Process image operations")

process_image_model = api.model(
    "ProcessImageModel",
    {
        "image": fields.String(required=True, description="Base64 encoded image"),
        "actions": fields.List(
            fields.String, required=True, description="Actions to perform on the image"
        ),
        "angle": fields.Integer(description="Angle to rotate the image"),
    },
)


@api.route("/", strict_slashes=False)
class ProcessImage(Resource):
    @api.expect(process_image_model)
    def post(self):
        data = request.get_json()
        image_base64 = data.get("image")
        actions = data.get("actions")
        angle = data.get("angle", 0)
        response_data = {}

        if not image_base64:
            return jsonify({"error": "Image data must be provided"}), 400

        # Decode base64 to numpy array
        img = decode_image_from_base64(image_base64)

        if "rotate" in actions:
            rotated_image = handle_rotation(img, angle)
            response_data["rotated_image"] = {
                "name": "rotated_image.jpg",
                "image": encode_image_to_base64(rotated_image),
            }

        cropped_images = [img]
        if "crop" in actions:
            blueprint = load_blueprint()
            cropped_images = handle_cropping(img, blueprint)
            response_data["cropped_images"] = [
                {
                    "name": f"cropped_image_{i+1}.jpg",
                    "image": encode_image_to_base64(cropped_image),
                }
                for i, cropped_image in enumerate(cropped_images)
            ]

        if "create_variants" in actions:
            all_variants = []
            for i, cropped_image in enumerate(cropped_images):
                variants = create_random_variants(cropped_image)
                all_variants.extend(
                    [
                        {
                            "name": f"cropped_image_{i+1}_variant_{j+1}.jpg",
                            "image": encode_image_to_base64(variant),
                        }
                        for j, variant in enumerate(variants)
                    ]
                )
            response_data["variants"] = all_variants

        log_message("Processed image successfully", "INFO")
        return jsonify(response_data)
