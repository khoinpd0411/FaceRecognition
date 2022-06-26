import os
from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper

base_dir = os.path.abspath(os.path.dirname(__name__))
config_path = os.path.join(base_dir, 'configs/yamls/detector_config.yaml')

class DetectorConfig:
    def __init__(self):
        configs = load(open(config_path, 'r'), Loader = Loader)
        
        self.MODEL_NAME = configs['MODEL_NAME']
        self.PRETRAINED_PATH = configs['PRETRAINED_PATH']
        self.INPUT_SIZE = configs['INPUT_SIZE']
        self.ALIGNED_SIZE = configs['ALIGNED_SIZE']

        self.CONF_THRESHOLD = configs['CONF_THRESHOLD']
        self.NMS_THRESHOLD = configs['NMS_THRESHOLD']
        # self.VIS_THRESHOLD = configs['VIS_THRESHOLD']
        self.TOP_K = configs['TOP_K']
        self.KEEP_TOP_K = configs['KEEP_TOP_K']
        self.MAX_BY_AREA = configs['MAX_BY_AREA']