from flask import Flask, jsonify, request 
from flask_marshmallow import Marshmallow 
from marshmallow import fields, ValidationError 
import mysql.connector
from mysql.connector import Error


app = Flask(__name__)
app.json.sort_keys=False

ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone_number = fields.String(required=True)
    credit_card = fields.String(required=True)
    
    class Meta:
        fields = ("name", "email", "phone_number", "credit_card")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

db_name = "fitness_tracker"
user = "root"
password = "Carmen!1994"
host = "localhost"

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )
        if conn.is_connected():
            print("Connected to db successfully.")
            return conn
        
    except Error as e:
        print(f"Error: {e}")
        return None
    
@app.route("/members", methods = ["GET"])
def get_members():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)   
     
    query = "SELECT * FROM Members"
    
    cursor.execute(query)
    
    members = cursor.fetchall()
    print(members)
    
    cursor.close()
    conn.close()
    
    return members_schema.jsonify(members)

@app.route('/members', methods=["POST"])
def add_member():
    member_data = member_schema.load(request.json)
    print(member_data)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    name = member_data['name']
    email = member_data['email']
    phone_number = member_data['phone_number']
    credit_card = member_data['credit_card']

    new_member = (name, email, phone_number, credit_card)
    print(new_member)
    
    query = "INSERT INTO Members(name, email, phone_number, credit_card) VALUES (%s, %s, %s, %s)"     
    
    cursor.execute(query, new_member)
    conn.commit()
    
    cursor.close()
    conn.close()
    return jsonify({"message": "New member has been added successfully"}), 201
    
        
@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        name = member_data['name']
        email = member_data['email']
        phone_number = member_data['phone_number']
        credit_card = member_data['credit_card']

        query = "UPDATE Members SET name = %s, email = %s, phone_number = %s, credit_card = %s WHERE member_id = %s"
        update_member = (name, email, phone_number, credit_card, id)
        cursor.execute(query, update_member)
        conn.commit()
        
        return jsonify({"message": "Member details updated successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"message": "Internal Server Error"}), 500 #server error- issue connecting to the server that the server cannot handle
    
    finally:
        # closing connection and cursor
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



@app.route("/members/<int:id>", methods=["DELETE"]) 
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500 
        cursor = conn.cursor()
        member_to_remove = (id,)
        

        query = "SELECT * FROM Members WHERE member_id = %s"
        cursor.execute(query, member_to_remove)
        member = cursor.fetchone() 
        if not member:
            return jsonify({"message": "Member not found"}), 404
        

        query = "SELECT * FROM workouts WHERE member_id = %s"
        cursor.execute(query, member_to_remove)
        workouts = cursor.fetchall()
        if workouts:
            return jsonify({"message": "Member has associated workouts, cannot delete until workouts cancelled"}), 400 

        query = "DELETE FROM Members WHERE member_id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()
        
        return jsonify({"message": "Member Removed Successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()




class WorkoutSchema(ma.Schema):
    workout_id = fields.Int(dump_only=True) # only for exposing - shows when we get it
    member_id = fields.Int(required=True) 
    activity = fields.Str(required=True)
    date = fields.Date(required=True)
   
    
    class Meta:
        fields = ("workout_id", "member_id", "activity", "date")
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)


@app.route('/workouts', methods=['POST'])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        query = "INSERT INTO Workouts (date, activity, member_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (workout_data['date'], workout_data['activity'], workout_data['member_id']))
        conn.commit()
        return jsonify({"message": "Workout added successfully"}), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/workouts', methods=['GET'])
def get_workouts():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Workouts")
    workouts = cursor.fetchall()
    cursor.close()
    conn.close()
    return workouts_schema.jsonify(workouts)       


@app.route("/workouts/<int:workout_id>", methods=["PUT"])
def update_workout(workout_id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": f"{err.messages}"}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database Connection Failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "UPDATE Workouts SET date = %s, activity = %s, member_id = %s WHERE workout_id = %s"
        date = workout_data["date"]
        activity = workout_data["activity"]
        member_id = workout_data["member_id"]
        updated_member = (date, activity, member_id)
        cursor.execute(query, updated_member)
        conn.commit()
        return jsonify({'message': "Workout was updated successfully"}), 200
    
    except Error as e:
        return jsonify({"error": f"{e}"}), 500
    
    finally:
        cursor.close()
        conn.close()


@app.route('/workouts/<int:workout_id>', methods=["DELETE"])
def delete_workout(workout_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "DELETE FROM Workouts WHERE workout_id = %s"
        cursor.execute(query, (workout_id,))
        return jsonify({"message": "Workout successfully deleted"}), 200
    
    except Error as e:
        return jsonify({"error": f"{e}"}), 500
    
    finally:
        cursor.close()
        conn.close()
    

if __name__ == "__main__":     
    app.run(debug=True) 








