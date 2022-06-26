import os
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper

base_dir = os.path.abspath(os.path.dirname(__name__))

if os.environ.get('API_ENV') == 'TEST':
    config_path = os.path.join(base_dir, 'configs/yamls/testing_config.yaml')
elif os.environ.get('API_ENV') == 'PROD':
    config_path = os.path.join(base_dir, 'configs/yamls/production_config.yaml')
else:
    config_path = os.path.join(base_dir, 'configs/yamls/development_config.yaml')

class Config:
    def __init__(self):
        configs = load(open(config_path,'r'), Loader= Loader)

        self.FLASK_ENV = configs['FLASK_ENV']
        self.DEBUG = configs['DEBUG']
        self.TESTING = configs['TESTING']
        self.FLASK_RUN_HOST = configs['FLASK_RUN_HOST']
        self.FLASK_RUN_PORT = configs['FLASK_RUN_PORT']
        self.URL_PREFIX = configs['URL_PREFIX']

        # Services
        self.FACE_DETECTOR = configs['FACE_DETECTOR']
        self.MIN_FACE_AREA = configs['MIN_FACE_AREA']

        self.FEATURE_EXTRACTOR = configs['FEATURE_EXTRACTOR']
        self.FACE_SEARCH = configs['FACE_SEARCH']
        self.COSINE_THRES = configs['COSINE_THRES']

        # Database
        self.SQLALCHEMY_COMMIT_ON_TEARDOWN = configs['SQLALCHEMY_COMMIT_ON_TEARDOWN']
        self.SQLALCHEMY_DATABASE_URI = configs['SQLALCHEMY_DATABASE_URI']

        # Device
        self.FACE_DETECTOR_DEVICE = configs['FACE_DETECTOR_DEVICE']
        self.FEATURE_EXTRACTOR_DEVICE = configs['FEATURE_EXTRACTOR_DEVICE']
        self.FACE_SEARCH_DEVICE = configs['FACE_SEARCH_DEVICE']
    
    def init_app(app):
        pass