from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import sys
import os

from configs import Config
from src.app.services import RetinaFaceDetector, ArcFaceExtractor

db = SQLAlchemy()
ma = Marshmallow()
base_config = Config()

def create_app(config):
    
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)                                                        # method to combine the FlaskApp and the third-libs
    ma.init_app(app)

    with app.app_context():
        current_app.face_detector = eval(config.FACE_DETECTOR)()
        current_app.feature_extractor = eval(config.FEATURE_EXTRACTOR)()

    url_prefix = config.URL_PREFIX
    from src.app.routers.Router import initialize_blueprint_router
    initialize_blueprint_router(app, url_prefix)

    # db.create_all()

    return app