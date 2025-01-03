from flask import Blueprint, jsonify, current_app

general_bp = Blueprint('general', __name__)

@general_bp.route('/version', methods=['GET'])
def get_version():
    return jsonify({
        "version": current_app.config['VERSION'],
        "status": "alpha",
        "api": "resume-backend"
    })

@general_bp.route('/health')
def health_check():
    return jsonify({
        "status": "up and running, boss"
    })