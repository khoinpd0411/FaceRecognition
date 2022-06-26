from flask import request, Blueprint, current_app as app

from configs import DetectorConfig, ExtractorConfig
from src.app.services import RetinafaceDetector, ArcFaceExtractor
from src.app.validators import FaceSearchValidator, FeatureExtractorValidator
from src.app.services.utils import decode_bs64
from src.app.services.retina.utils.face_align import norm_crop
from src.app.handlers import response_with
from src.app.handlers import responses as resp
from configs import Config
import time

face_routes = Blueprint('face_routes', __name__)

config = Config()
extractor_config = ExtractorConfig()
detector_config = DetectorConfig()

@face_routes.route('/face/extract', methods = ['POST'])
def extract_features(imgs):
    start = time.time()
    outputs = {}
    validator = FeatureExtractorValidator()

    data = request.get_json()['data']
    try:
        validator.load(data)
    except:
        return response_with(resp.INVALID_INPUT_422)

    try:
        imgs_bs64 = data.get('image')
        if len(imgs_bs64 > extractor_config.EMBEDDING_BATCHSIZE):
            return response_with(resp.BAD_REQUEST_400, message = 'Too many images to handle')

        imgs = []
        for img_bs64 in imgs_bs64:
            imgs.append(decode_bs64(img_bs64))

        dets_list, landms_list, _= app.face_detector.detect(imgs)

        for i, dets in enumerate(dets_list):
            feature = None
            if (len(dets) == 0) or (len(dets) > 1):
                pass
            elif dets[0][4] < detector_config.CONF_THRESHOLD:
                pass
            else:
                align_face = norm_crop(imgs[i], landms_list[i])
                feature = app.feature_extractor.extract(align_face)
        
            value = {
                'face': {
                    'location': dets[0][:4],
                    'conf': dets[0][4],
                    'embedding': feature.tolist() if feature else None
                },
            }

            outputs.update({i : value})

        return response_with(resp.SUCCESS_200, value = outputs)
    except:
        return response_with(resp.BAD_REQUEST_400)
