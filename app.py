from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import check_password_hash

app = Flask(__name__)
CORS(app)

# Configuration for MySQL Database
app.config['MYSQL_HOST'] = '140.238.244.101'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1lnli9uELkeWC7GfUQF01an3Yevq7wXbpkM7vskAyMI652tRhUnin4e8gD4DUOjy'  # Be cautious with passwords!
app.config['MYSQL_DB'] = 'we2'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')
    
    
users = {
    "user1": "pbkdf2:sha256:150000$Wf3u9jeI$..."
    # The value here should be a hash of the actual password
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user_password_hash = users.get(username)

    if user_password_hash and check_password_hash(user_password_hash, password):
        # If the username and password match, create and return a token
        # In a real application, you'd create a token here
        return jsonify({"token": "your_generated_token_here"}), 200
    else:
        # Invalid username or password
        return jsonify({"error": "Invalid username or password"}), 401    

@app.route('/data')
def get_data():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM stations")
    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    return jsonify(results)
    
# New test route
@app.route('/test', methods=['POST'])
def test():
    return jsonify({"message": "Hello"})

@app.route('/add-station', methods=['POST'])
def add_station():
    data = request.get_json()
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT 1 FROM stations WHERE number = %s", (data['number'],))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Station with this number already exists"}), 409  # HTTP 409 Conflict

    banking = data.get('banking') == 'true'

    banking = data.get('banking') == 'true'
    bonus = data.get('bonus') == 'true'
    status = data.get('status', 'CLOSED')  # Use 'CLOSED' as default if not provided

    # Try parsing the last_update, if provided and in correct format
    try:
        if 'last_update' in data:
            last_update = datetime.strptime(data['last_update'], '%Y-%m-%d %H:%M:%S')
        else:
            last_update = datetime.now()  # Use current time if not provided
    except ValueError:
        # If there's an error in parsing last_update, return an error
        return jsonify({"error": "Invalid date format for 'last_update'"}), 400

    query = """
    INSERT INTO stations (number, name, address, position_lat, position_lng, banking, bonus, status, contract_name, bike_stands, available_bike_stands, available_bikes, last_update) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(query, (
            data['number'],
            data['name'],
            data['address'],
            data['position_lat'],
            data['position_lng'],
            banking,
            bonus,
            status,
            data['contract_name'],
            data['bike_stands'],
            data['available_bike_stands'],
            data['available_bikes'],
            last_update
        ))
        mysql.connection.commit()
    except mysql.connection.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()

    return jsonify({"message": "Station added successfully"}), 201
    
  
  # edit station endpoint 

@app.route('/edit-station/<int:station_id>', methods=['PUT'])
def edit_station(station_id):
    data = request.get_json()
    cursor = mysql.connection.cursor()
    query = """
    UPDATE stations SET 
    name = %s, address = %s, position_lat = %s, position_lng = %s, banking = %s, bonus = %s, status = %s, contract_name = %s, bike_stands = %s, available_bike_stands = %s, available_bikes = %s, last_update = %s 
    WHERE number = %s
    """
    cursor.execute(query, (data['name'], data['address'], data['position_lat'], data['position_lng'], data['banking'], data['bonus'], data['status'], data['contract_name'], data['bike_stands'], data['available_bike_stands'], data['available_bikes'], data['last_update'], station_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Station updated successfully"}), 200

@app.route('/delete-station/<int:station_id>', methods=['DELETE'])
def delete_station(station_id):
    # Assuming 'station_id' corresponds to the 'number' field in your 'stations' table.
    cursor = mysql.connection.cursor()
    try:
        query = "DELETE FROM stations WHERE number = %s"
        cursor.execute(query, (station_id,))
        mysql.connection.commit()
        # Check if the delete operation was successful
        if cursor.rowcount == 0:
            return jsonify({"error": "Station not found"}), 404
        else:
            return jsonify({"message": "Station deleted successfully"}), 200
    except Exception as e:
        mysql.connection.rollback()  # Roll back the transaction on error
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


if __name__ == '__main__':
    app.run(debug=True)
