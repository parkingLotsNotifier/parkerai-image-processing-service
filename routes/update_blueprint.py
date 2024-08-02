from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from utils.blueprint_utils import save_blueprint
from utils.firebase_logger import log_message

api = Namespace('update_blueprint', description='Update blueprint operations')

update_blueprint_model = api.model('UpdateBlueprintModel', {
    'blueprint': fields.Raw(required=True, description='Updated blueprint JSON')
})

@api.route('/', strict_slashes=False)
class UpdateBlueprint(Resource):
    @api.expect(update_blueprint_model)
    def post(self):
        data = request.get_json()
        blueprint = data.get('blueprint')

        if not blueprint:
            return jsonify({'error': 'Blueprint data must be provided'}), 400

        save_blueprint(blueprint)
        log_message("Blueprint updated successfully", "INFO")
        return jsonify({'message': 'Blueprint updated successfully'})
