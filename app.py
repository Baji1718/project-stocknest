from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 🔥 Enable CORS for all routes

materials = [
    {
        "MaterialName": "Vanilla Extract",
        "UOM": "Ltr",
        "Description": "Used in vanilla ice cream"
    },
    {
        "MaterialName": "Waffle Cone",
        "UOM": "Pcs",
        "Description": "Cone for serving ice cream"
    }
    ,{
        "MaterialName": "Vanilla Extract",
        "UOM": "Ltr",
        "Description": "Used in vanilla ice cream"
    },
    {
        "MaterialName": "Waffle Cone",
        "UOM": "Pcs",
        "Description": "Cone for serving ice cream"
    },
    {
        "MaterialName": "Vanilla Extract",
        "UOM": "Ltr",
        "Description": "Used ------in vanilla ice cream"
    }
]

@app.route('/api/materials', methods=['GET'])
def get_materials():
    return jsonify(materials)

if __name__ == '__main__':
    app.run()
