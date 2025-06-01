from flask import request, jsonify
from flask_login import login_user, logout_user, current_user
from models import db, User, Advertisement
from auth import login_required, owner_required

def init_routes(app):
    # Регистрация
    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password required"}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
        
        user = User(email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created"}), 201
    
    # Логин
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()
        
        if not user or not user.check_password(data.get('password')):
            return jsonify({"error": "Invalid credentials"}), 401
        
        login_user(user)
        return jsonify({"message": "Logged in"})
    
    # Получение всех объявлений
    @app.route('/ads', methods=['GET'])
    def get_all_ads():
        ads = Advertisement.query.all()
        return jsonify([ad.to_dict() for ad in ads]), 200

    # Получение конкретного объявления
    @app.route('/ads/<int:ad_id>', methods=['GET'])
    def get_ad(ad_id):
        ad = Advertisement.query.get_or_404(ad_id)
        return jsonify(ad.to_dict()), 200

    # Создание объявления
    @app.route('/ads', methods=['POST'])
    @login_required
    def create_ad():
        data = request.get_json()
        new_ad = Advertisement(
            title=data['title'],
            description=data['description'],
            owner_id=current_user.id
        )
        db.session.add(new_ad)
        db.session.commit()
        return jsonify(new_ad.to_dict()), 201

    # Удаление объявления
    @app.route('/ads/<int:ad_id>', methods=['DELETE'])
    @login_required
    @owner_required
    def delete_ad(ad_id):
        ad = Advertisement.query.get_or_404(ad_id)
        db.session.delete(ad)
        db.session.commit()
        return jsonify({"message": "Advertisement deleted"}), 200