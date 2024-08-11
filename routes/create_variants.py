from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import decode_image_from_base64, encode_image_to_base64
from utils.variant_utils import create_random_variants
from utils.firebase_logger import log_message

api = Namespace("create_variants", description="Create image variants operations")

create_variants_model = api.model(
    "CreateVariantsModel",
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
    },
)

create_variants_response_model = api.model(
    "CreateVariantsResponseModel",
    {
        "variants": fields.List(
            fields.Nested(
                api.model(
                    "VariantImage",
                    {
                        "name": fields.String(
                            description="Name of the variant image",
                            example="example_image_variant_1.jpg",
                        ),
                        "image": fields.String(
                            description="Base64 encoded variant image",
                            example="<base64_variant_image_string>",
                        ),
                    },
                )
            )
        )
    },
)


@api.route("/", strict_slashes=False)
class CreateVariants(Resource):
    @api.expect(create_variants_model)
    @api.response(200, "Success", create_variants_response_model)
    def post(self):
        data = request.get_json()
        image_name = data.get("image_name")
        image_base64 = data.get("image")

        if not image_base64:
            return jsonify({"error": "Image data must be provided"}), 400

        # Decode base64 to numpy array
        img = decode_image_from_base64(image_base64)

        # Create variants
        variants = create_random_variants(img)

        # Generate names for variants based on the original image name
        base_name = image_name.rsplit(".", 1)[0]
        extension = image_name.rsplit(".", 1)[1]
        variants_response = [
            {
                "name": f"{base_name}_variant_{i+1}.{extension}",
                "image": encode_image_to_base64(variant),
            }
            for i, variant in enumerate(variants)
        ]

        log_message("Created image variants successfully", "INFO")
        return jsonify({"variants": variants_response})
