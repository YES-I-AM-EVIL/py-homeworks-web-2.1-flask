from flask import jsonify
from flask_login import current_user
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(ad_id, *args, **kwargs):
        from models import Advertisement
        ad = Advertisement.query.get_or_404(ad_id)
        if ad.owner_id != current_user.id:
            return jsonify({"error": "Forbidden: Not the owner"}), 403
        return f(ad_id, *args, **kwargs)
    return decorated_function