from src.app.controllers.v1.DBController import database_routes
from src.app.controllers.v1.FaceController import face_routes

def initialize_blueprint_router(app, url_prefix = ''):
    app.register_blueprint(database_routes, url_prefix = url_prefix)
    app.register_blueprint(face_routes, url_prefix = url_prefix)