from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from datetime import timedelta

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Användarnamn upptaget'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'E-postadress upptagen'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Användare skapad'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=1)
        )
        return jsonify({
            'access_token': access_token,
            'user_id': user.id,
            'username': user.username
        })

    return jsonify({'error': 'Ogiltigt användarnamn eller lösenord'}), 401

@auth.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    print(user_id)
    user = User.query.get(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

