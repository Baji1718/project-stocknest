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
        return {"message": str(e)}

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
        return jsonify({'message': str(e)}), 500

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
        return {"message": str(e)}

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
        return jsonify({'message': str(e)}), 500

# ✅ Inventory fetcher
def get_inventory_from_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT materialname, quantity FROM inventory")
        rows = cursor.fetchall()
        inventory = [
            {
                "MaterialName": row[0],
                "Quantity": float(row[1])
            }
            for row in rows
        ]
        cursor.close()
        conn.close()
        return inventory
    except Exception as e:
        return {"message": str(e)}

# ✅ Inventory API
@app.route('/api/inventory', methods=['GET'])
def inventory():
    result = get_inventory_from_db()
    return jsonify(result)

# ✅ Delivery order API
@app.route('/api/delivery-order', methods=['POST'])
def delivery_order():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Call the stored procedure with the JSON input
        cursor.execute("SELECT process_delivery_order(%s)", (json.dumps(data),))
        result = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': result}), 200

    except psycopg2.Error as db_error:
        # Return detailed database error if it's a raised exception from the procedure
        return jsonify({'message': str(db_error).split('\n')[0]}), 400

    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({'message': str(e)}), 500

@app.route('/api/delivery-order-summary', methods=['GET'])
def delivery_order_summary():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Call your stored procedure that returns delivery order summary
        cursor.execute("SELECT * FROM get_all_delivery_order_summary()")
        rows = cursor.fetchall()
        
        # Format the response as list of dicts
        summary = [
            {
                "DeliveryOrderName": row[0],
                "TotalItems": int(row[1]),
                "TotalQuantity": float(row[2])
            }
            for row in rows
        ]
        
        cursor.close()
        conn.close()
        
        return jsonify(summary), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/delivery-order-details', methods=['POST'])
def delivery_order_details():
    try:
        data = request.get_json()
        delivery_order_name = data.get('DeliveryOrderName')
        if not delivery_order_name:
            return jsonify({'message': 'DeliveryOrderName is required'}), 400
        
        # Prepare JSON input as expected by the SP (JSON array with one object)
        json_input = json.dumps([{"DeliveryOrderName": delivery_order_name}])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Call the stored procedure with the JSON input
        cursor.execute("SELECT * FROM get_delivery_order_details(%s)", (json_input,))
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
        return jsonify({'message': str(e)}), 500



# ✅ Run server
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
