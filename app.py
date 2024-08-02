from concurrent.futures import thread
from flask import Flask
from flask_restx import Api
from routes.crop import api as crop_api
from routes.update_blueprint import api as update_blueprint_api
from routes.average_intensity import api as average_intensity_api
from routes.rotate import api as rotate_api
from routes.create_variants import api as create_variants_api
from routes.process_image import api as process_image_api
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='/config/.env')

app = Flask(__name__)
api = Api(app, version='1.0', title='Image Processing API', description='A simple Image Processing API')

# Register namespaces with updated paths
api.add_namespace(crop_api, path='/image-processing/crop')
api.add_namespace(update_blueprint_api, path='/image-processing/update-blueprint')
api.add_namespace(average_intensity_api, path='/image-processing/average-intensity')
api.add_namespace(rotate_api, path='/image-processing/rotate')
api.add_namespace(create_variants_api, path='/image-processing/create-variants')
api.add_namespace(process_image_api, path='/image-processing/process')

if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', '3002'))
    app.run(host=host, port=port, threaded = True)

