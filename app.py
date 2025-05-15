from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ PostgreSQL connection details (use your actual values in production)
DB_HOST = '43.205.147.184'
DB_PORT = '5432'
DB_NAME = 'Practice'
DB_USER = 'Skubiq_Dev'
DB_PASSWORD = 'AVyaINV&!222@1'  # Default; change if needed

def get_materials_from_db():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        # Run the SELECT query
        cursor.execute("SELECT materialname, description, uom FROM Material WHERE IsDeleted = FALSE")
        rows = cursor.fetchall()
        # Format the results as a list of dictionaries
        materials = [
            {
                "MaterialName": row[0],
                "Description": row[1],
                "UOM": row[2]
            }
            for row in rows
        ]
        cursor.close()
        conn.close()
        return materials
    except Exception as e:
        return {"error": str(e)}

# API route to return material data
@app.route('/api/materials', methods=['GET'])
def get_materials():
    data = get_materials_from_db()
    return jsonify(data)



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
