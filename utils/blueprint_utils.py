import json
import os

def load_blueprint():
    with open('./config/blueprint.json', 'r') as f:
        blueprint = json.load(f)
    return blueprint

def save_blueprint(blueprint):
    with open('./config/blueprint.json', 'w') as f:
        json.dump(blueprint, f)

