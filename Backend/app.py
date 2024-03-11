from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration for MySQL Database
app.config['MYSQL_HOST'] = '140.238.244.101'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1lnli9uELkeWC7GfUQF01an3Yevq7wXbpkM7vskAyMI652tRhUnin4e8gD4DUOjy'
app.config['MYSQL_DB'] = 'we2'

mysql = MySQL(app)


@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask MySQL app!"})


@app.route('/data')
def get_data():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT number, name, address, position_lat,position_lng, banking, bonus, status, contract_name, bike_stands, available_bike_stands, available_bikes, last_update FROM stations")  # Adjust your SELECT query based on the actual column names
    columns = [column[0] for column in cursor.description]
    results = []

    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    cursor.close()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
