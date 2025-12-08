from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for demonstration purposes
# In a real application, this would be replaced with a database
users_data = []

@app.route('/register', methods=['POST'])
def register_user():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    other_info = request.json.get('other_info', None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # In a real application, you would hash the password before storing it
    user = {
        "username": username,
        "password": password,  # Store hashed password in production
        "other_info": other_info
    }
    users_data.append(user)
    print(f"New user registered: {user}") # For debugging

    return jsonify({"msg": "User registered successfully", "user": {"username": username, "other_info": other_info}}), 201

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users_data), 200

@app.route('/login', methods=['POST'])
def login_user():
    if not request.is_json:
        return jsonify({"success": False, "message": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({"success": False, "message": "Missing username or password"}), 400

    user_found = None
    for user in users_data:
        if user["username"] == username and user["password"] == password:
            user_found = user
            break

    if user_found:
        return jsonify({"success": True, "message": f"登录成功！欢迎回来，{username}！", "user": {"username": username}}), 200
    else:
        return jsonify({"success": False, "message": "用户名或密码不正确"}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)