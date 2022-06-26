import argparse
import torch
import torch.backends.cudnn as cudnn
import numpy as np
import sys
import cv2
import time

from configs import Config, DetectorConfig
from src.app.services.retina.data import cfg_mnet, cfg_re50
from src.app.services.retina.layers.functions.prior_box import PriorBox
from src.app.services.retina.models.retinaface import RetinaFace
from src.app.services.retina.utils.nms.py_cpu_nms import py_cpu_nms
from src.app.services.retina.utils.box_utils import decode
from src.app.services.retina.utils.face_align import norm_crop
from src.app.services.utils import load_model, get_device, resize_img, convert_for_inference, get_max_by_area

class RetinaFaceDetector:
    def __init__(self):
        self.config = Config()
        self.detector_config = DetectorConfig()
        self.device = get_device(self.config.FACE_DETECTOR_DEVICE, 0)

        if self.detector_config.MODEL_NAME == 'mnet':
            self.cfg = cfg_mnet
            self.cfg.update({'pretrained_path': './weights/mobilenetV1X0.25_pretrain.tar'})
            print(self.cfg)
        else:
            self.cfg = cfg_re50
            self.cfg.update({'pretrained_path': './weights/MSMV1_Resnet50.pth'})
        self.model = RetinaFace(cfg = self.cfg, phase = 'test')
        self.model = load_model(self.model, self.detector_config.PRETRAINED_PATH, self.device)
        self.model.eval()
        self.model.to(self.device)

        self.scale = torch.Tensor([self.detector_config.INPUT_SIZE[1],
                                self.detector_config.INPUT_SIZE[0],
                                self.detector_config.INPUT_SIZE[1],
                                self.detector_config.INPUT_SIZE[0]]).to(self.device)
        
        
    
    def preprocess(self, images):
        rsz_img_list = None
        ratio_list = []

        for img in images:
            rsz_img, ratio = resize_img(img, self.detector_config.INPUT_SIZE)
            rsz_img = convert_for_inference(rsz_img)
            
            if rsz_img_list is None:
                rsz_img_list = rsz_img
            else:
                rsz_img_list = torch.vstack((rsz_img_list, rsz_img))
            ratio_list.append(ratio)
        
        return rsz_img_list, ratio_list
    
    def inference(self, images):
        with torch.no_grad():
            images = images.to(self.device)
            outputs = self.model(images)
            return outputs
    
    def postprocess(self, outputs, ratio_list, max_by_area):
        areas_list = []
        landms_list = []
        dets_list = []
        
        for i, output in enumerate(outputs):
            if output is not None:
                loc, conf, landms = output

                priorbox = PriorBox(self.cfg, image_size=self.detector_config.INPUT_SIZE)
                priors = priorbox.forward()
                priors = priors.to(self.device)
                prior_data = priors.data

                boxes = decode(loc.data.squeeze(0), prior_data, self.cfg['variance'])
                boxes = boxes * self.scale
                boxes = boxes.cpu().numpy()

                scale1 = torch.Tensor([self.detector_config.INPUT_SIZE[1], self.detector_config.INPUT_SIZE[0],
                                    self.detector_config.INPUT_SIZE[1], self.detector_config.INPUT_SIZE[0],
                                    self.detector_config.INPUT_SIZE[1], self.detector_config.INPUT_SIZE[0],
                                    self.detector_config.INPUT_SIZE[1], self.detector_config.INPUT_SIZE[0],
                                    self.detector_config.INPUT_SIZE[1], self.detector_config.INPUT_SIZE[0]])
                scale1 = scale1.to(self.device)
                landms = landms * scale1
                landms = landms.cpu().numpy()

                # ignore low scores
                scores = conf.squeeze(0).data.cpu().numpy()[:, 1]
                inds = np.where(scores > self.detector_config.CONF_THRESHOLD)[0]
                boxes = boxes[inds]
                landms = landms[inds]
                scores = scores[inds]

                # keep top-K before NMS
                order = scores.argsort()[::-1][:self.detector_config.TOP_K]
                boxes = boxes[order]
                landms = landms[order]
                scores = scores[order]

                # do NMS
                dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
                keep = py_cpu_nms(dets, self.detector_config.NMS_THRESHOLD)
                dets = dets[keep, :]
                landms = landms[keep]

                # keep top-K faster NMS
                dets = dets[:self.detector_config.KEEP_TOP_K, :]
                landms = landms[:self.detector_config.KEEP_TOP_K, :]

                dets = [[(int(b/ratio_list[j]) if j != 4 else b) for j, b in enumerate(bbox)] for bbox in dets]
                landms = [[int(p/ratio_list) for p in landm] for landm in landms]

                if max_by_area:
                    det, landm, area = get_max_by_area(dets, landms)
                    areas_list.append(area)
                    dets_list.append(det)
                    landms_list.append(landm)
                else:
                    dets_list.append(dets)
                    landms_list.append(landms)
        return dets_list, landms_list, areas_list

    def detect(self, images):
        img_rszs, ratio_list = self.preprocess(images)
        outputs = self.inference(img_rszs)
        dets_list, landms_list, areas_list = self.postprocess(outputs, ratio_list, self.detector_config.MAX_BY_AREA)

        return dets_list, landms_list, areas_list

if __name__ == '__main__':
    img_path = '/home/khoi/Code/Projects/FaceRecognition/Pytorch_Retinaface/curve/test.jpg'
    detector = RetinafaceDetector()
    img = cv2.imread(img_path)
    crop_faces_list = detector.detect(img)
    print(len(crop_faces_list))