from flask import Flask

from .extensions import cors
from .routes.general import general_bp
from .routes.analyze import analysis_bp
from .routes.resume import resume_bp
from .routes.conversion import conversion_bp

import logging
import sys


def create_app():
    app = Flask(__name__)

    app.config['VERSION'] = "0.1.0"
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB

    cors.init_app(app, resources={
        r"/*": {
            "origins": [
                "https://resume-updater-flax.vercel.app",
                "http://localhost:3000"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = app.logger
    logger.setLevel(logging.DEBUG)

    app.register_blueprint(general_bp)
    app.register_blueprint(analysis_bp, url_prefix='/analyze')
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(conversion_bp, url_prefix='/convert')

    return app
