from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import (
    decode_image_from_base64,
    encode_image_to_base64,
    handle_cropping,
)
from utils.blueprint_utils import (
    generate_filenames,
    update_response_with_crops,
    insert_filenames_into_response,
)
from utils.firebase_logger import log_message
from utils.database_utils import fetch_blueprint


api = Namespace("crop", description="Crop image operation")

crop_image_model = api.model(
    "CropImageModel",
    {
        "image": fields.String(
            required=True,
            description="Base64 encoded image",
            example="<base64_image_string>",
        ),
        "image_name": fields.String(
            required=True, description="Name of the image", example="example_image.jpg"
        ),
        "camera_id": fields.String(
            required=True,
            description="ID of the camera to fetch blueprint",
            example="64a9c8f4ef1f9f5a8b5d0a6d",
        ),
    },
)

coordinate_model = api.model(
    "Coordinate",
    {
        "x1": fields.Float(description="X1 coordinate", example=10.5),
        "y1": fields.Float(description="Y1 coordinate", example=20.5),
        "w": fields.Float(description="Width of the cropped area", example=200.0),
        "h": fields.Float(description="Height of the cropped area", example=150.0),
    },
)

crop_image_response_model = api.model(
    "CropImageResponseModel",
    {
        "file_name": fields.String(
            required=True, description="Name of the image", example="example_image.jpg"
        ),
        "slots": fields.List(
            fields.Nested(
                api.model(
                    "Slot",
                    {
                        "average_intensity": fields.Float(
                            description="Average intensity of the cropped image",
                            example=128.5,
                        ),
                        "coordinate": fields.Nested(
                            coordinate_model,
                            description="Coordinates of the cropped area",
                        ),
                        "file_name": fields.String(
                            description="Filename of the processed image",
                            example="example_image_crop_1.jpg",
                        ),
                        "lot_name": fields.String(
                            description="Lot name os the current parking slot",
                            example="A1",
                        ),
                        "roi": fields.String(
                            description="Base64 encoded cropped image",
                            example="<base64_cropped_image_string>",
                        )
                    },
                )
            )
        ),
    },
)


@api.route("/", strict_slashes=False)
class CropImage(Resource):
    @api.expect(crop_image_model)
    @api.response(200, "Success", crop_image_response_model)
    def post(self):
        data = request.json
        camera_id = data.get("camera_id")
        image_name = data.get("image_name")
        image = data.get("image")

        if not camera_id or not image_name or not image:
            return (
                jsonify({"error": "camera_id, image_name, and image are required"}),
                400,
            )

        image = decode_image_from_base64(image)

        # Step 1: Data Preparation
        blueprint = fetch_blueprint(camera_id)

        # Step 2: Generate Filenames for Cropped Images
        filenames = generate_filenames(image_name, len(blueprint.get("slots", [])))

        # Step 3: Insert Filenames into Blueprint
        response = insert_filenames_into_response(blueprint, filenames, image_name)

        # Step 4: Perform Cropping
        cropped_images = handle_cropping(image, response)

        # Step 5: Encode cropped images to Base64
        encoded_cropped_images = [encode_image_to_base64(img) for img in cropped_images]

        # Step 6: Update Blueprint with Cropped Images
        response = update_response_with_crops(response, encoded_cropped_images)

        log_message("Cropped image successfully", "INFO")
        return jsonify(response)
