from pydoc import describe
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.image_utils import (
    decode_image_from_base64,
    handle_cropping,
    handle_rotation,
    encode_image_to_base64,
    calculate_average_intensity,
)
from utils.blueprint_utils import (
    insert_filenames_into_response,
    update_response_with_crops,
    generate_filenames,
)
from utils.database_utils import fetch_blueprint
from utils.firebase_logger import log_message

api = Namespace("process", description="Process image operations")

process_image_model = api.model(
    "ProcessImageModel",
    {
        "image": fields.String(required=True, description="Base64 encoded image", example="<base64_image_string>"),
        "image_name": fields.String(required=True, description="Name of the image", example="example_image.jpg"),
        "actions": fields.List(
            fields.String,
            required=False,
            description="Actions to perform on the image (rotate, crop, etc.)",
            example=["rotate", "crop", "average_intensity"]
        ),
        "angle": fields.Integer(description="Angle to rotate the image", example=90),
        "camera_id": fields.String(
            required=True, description="ID of the camera to fetch blueprint", example="64a9c8f4ef1f9f5a8b5d0a6d"
        ),
    },
)

coordinate_model = api.model('Coordinate', {
    'x1': fields.Float(description='X1 coordinate', example=10.5),
    'y1': fields.Float(description='Y1 coordinate', example=20.5),
    'w': fields.Float(description='Width of the cropped area', example=200.0),
    'h': fields.Float(description='Height of the cropped area', example=150.0)
})

process_image_response_model = api.model('ProcessImageResponseModel', {
    'file_name' : fields.String(required=True, description="Name of the image", example="example_image.jpg"),
    'slots': fields.List(fields.Nested(api.model('Slot', {
        'average_intensity': fields.Float(description='Average intensity of the cropped image', example=128.5),
        'coordinate': fields.Nested(coordinate_model, description='Coordinates of the cropped area'),
        'file_name': fields.String(description='Filename of the processed image', example='example_image_crop_1.jpg'),
        'lot_name': fields.String(description='Lot name os the current parking slot', example='A1'),
        'roi': fields.String(description='Base64 encoded cropped image', example='<base64_cropped_image_string>'),
        'variants': fields.List(fields.String(description='Base64 encoded cropped image', example='<base64_variant_image_string>'), description='List of variants', example=[])
    })))
})

@api.route("/", strict_slashes=False)
class ProcessImage(Resource):
    @api.expect(process_image_model)
    @api.response(200, 'Success', process_image_response_model)
    def post(self):
        try:
            data = request.get_json()
            image_base64 = data.get("image")
            image_name = data.get("image_name")
            actions = data.get("actions", [])  # Default to an empty list
            angle = data.get("angle", 0)
            camera_id = data.get("camera_id")

            if not image_base64 or not camera_id:
                return (
                    jsonify({"error": "Image data and camera ID must be provided"}),
                    400,
                )

            # Decode base64 to numpy array
            img = decode_image_from_base64(image_base64)

            # Fetch the blueprint from the database
            blueprint = fetch_blueprint(camera_id)

            # If actions are empty, perform all available actions
            if not actions:
                actions = ["rotate", "crop", "average_intensity"]

            # Process each action in the order provided
            cropped_images = []
            for action in actions:
                if action == "rotate":
                    img = handle_rotation(img, angle)
                elif action == "crop":
                    filenames = generate_filenames(
                        image_name, len(blueprint.get("slots", []))
                    )
                    response = insert_filenames_into_response(blueprint, filenames, image_name)
                    cropped_images = handle_cropping(img, blueprint)
                    encoded_cropped_images = [
                        encode_image_to_base64(img) for img in cropped_images
                    ]
                    response = update_response_with_crops(
                        blueprint, encoded_cropped_images
                    )
                    if cropped_images:
                        img = cropped_images[0]
                elif action == "average_intensity":
                    if "crop" in actions:
                        for i, cropped_image in enumerate(cropped_images):
                            intensity = calculate_average_intensity(cropped_image)
                            response["slots"][i]["average_intensity"] = intensity

            log_message("Processed image and updated blueprint successfully", "INFO")
            return jsonify(response)

        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": "An error occurred: " + str(e)}), 500
