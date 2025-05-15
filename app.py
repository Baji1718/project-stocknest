from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ PostgreSQL connection details
DB_HOST = '43.205.147.184'
DB_PORT = '5432'
DB_NAME = 'Practice'
DB_USER = 'Skubiq_Dev'
DB_PASSWORD = 'AVyaINV&!222@1'  # For production, secure this value!

# ✅ Reusable database connection helper
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# ✅ Material master fetcher
def get_materials_from_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT materialname, description, uom FROM Material WHERE IsDeleted = FALSE")
        rows = cursor.fetchall()
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

# ✅ Material master API
@app.route('/api/materials', methods=['GET'])
def get_materials():
    data = get_materials_from_db()
    return jsonify(data)

# ✅ Inward order API
@app.route('/api/inward-order', methods=['POST'])
def inward_order():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT process_inward_order(%s)", (json.dumps(data),))
        result = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Order summary fetcher
def get_order_summary_from_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM get_all_order_summary()")
        rows = cursor.fetchall()
        summary = [
            {
                "OrderName": row[0],
                "TotalItems": int(row[1]),
                "TotalQuantity": float(row[2])
            }
            for row in rows
        ]
        cursor.close()
        conn.close()
        return summary
    except Exception as e:
        return {"error": str(e)}

# ✅ Order summary API
@app.route('/api/order-summary', methods=['GET'])
def order_summary():
    result = get_order_summary_from_db()
    return jsonify(result)

# ✅ Order details API
@app.route('/api/order-details', methods=['POST'])
def order_details():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM get_order_details(%s)", (json.dumps(data),))
        rows = cursor.fetchall()
        details = [
            {
                "MaterialName": row[0],
                "Quantity": float(row[1])
            }
            for row in rows
        ]
        cursor.close()
        conn.close()
        return jsonify(details), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Run server
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
