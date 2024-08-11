from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import (
    decode_image_from_base64,
    handle_rotation,
    encode_image_to_base64,
)
from utils.firebase_logger import log_message

api = Namespace("rotate", description="Rotate image operations")

rotate_model = api.model(
    "RotateModel",
    {
        "image": fields.String(
            required=True,
            description="Base64 encoded image",
            example="<base64_image_string>",
        ),
        "image_name": fields.String(
            required=True,
            description="Name of the image",
            example="example_image.jpg",
        ),
        "angle": fields.Integer(
            required=True, description="Angle to rotate the image", example=90
        ),
    },
)

rotate_response_model = api.model(
    "RotateResponseModel",
    {
        "rotated_image": fields.Nested(
            api.model(
                "RotatedImage",
                {
                    "name": fields.String(
                        description="Name of the rotated image",
                        example="example_image_rotated.jpg",
                    ),
                    "image": fields.String(
                        description="Base64 encoded rotated image",
                        example="<base64_rotated_image_string>",
                    ),
                },
            )
        )
    },
)


@api.route("/", strict_slashes=False)
class RotateImage(Resource):
    @api.expect(rotate_model)
    @api.response(200, "Success", rotate_response_model)
    def post(self):
        data = request.get_json()
        image_name = data.get("image_name")
        image_base64 = data.get("image")
        angle = data.get("angle")

        if not image_base64:
            return jsonify({"error": "Image data must be provided"}), 400

        # Decode base64 to numpy array
        img = decode_image_from_base64(image_base64)

        # Perform rotation
        rotated_image = handle_rotation(img, angle)

        # Encode back to base64
        encoded_image = encode_image_to_base64(rotated_image)

        # Generate the rotated image name based on the original image name
        rotated_image_name = f"{image_name.rsplit('.', 1)[0]}_rotated.{image_name.rsplit('.', 1)[1]}"

        log_message("Rotated image successfully", "INFO")
        return jsonify(
            {"rotated_image": {"name": rotated_image_name, "image": encoded_image}}
        )
