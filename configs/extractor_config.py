import os
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper

base_dir = os.path.abspath(os.path.dirname(__name__))
config_path = os.path.join(base_dir, 'configs/yamls/extractor_config.yaml')

class ExtractorConfig:
    def __init__(self):
        configs = load(open(config_path, 'r'), Loader = Loader)

        self.MODEL_NAME = configs['MODEL_NAME']
        self.PRETRAINED_PATH = configs['PRETRAINED_PATH']
        self.ALIGN_OUTPUT = configs['ALIGN_OUTPUT']
        self.EMBEDDING_BATCHSIZE = configs['EMBEDDING_BATCHSIZE']