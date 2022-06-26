import argparse
from sklearn import preprocessing
import cv2
import numpy as np
import torch
import sys

sys.path.append('./src/app/services/')

from configs import Config, ExtractorConfig
from src.app.services.arcface.backbones import *
from src.app.services.utils import load_model, get_device

class ArcFaceExtractor:
    def __init__(self):
        self.config = Config()
        self.extractor_config = ExtractorConfig()
        self.device = get_device(self.config.FEATURE_EXTRACTOR_DEVICE, 0)
        self.model = eval("{}".format(self.extractor_config.MODEL_NAME))
        self.model = load_model(self.model, self.extractor_config.PRETRAINED_PATH, self.device)
        self.model.eval()
        self.model.to(self.device)
        self.batch_size = self.extractor_config.EMBEDDING_BATCHSIZE
    
    def preprocess(self, images):
        aligned_faces = None
        for i, image in enumerate(images):
            tmp_face = image.transpose(2, 0, 1)
            tmp_face = torch.from_numpy(tmp_face).unsqueeze(0)
            
            if aligned_faces is None:
                aligned_faces = tmp_face
            else:
                aligned_faces = torch.vstack((aligned_faces, tmp_face))

        return aligned_faces
    
    def inference(self, aligned_faces):
        aligned_faces = aligned_faces.to(self.device)
        aligned_faces.div_(255).sub_(0.5).div_(0.5)
        face_embeddings = None
        with torch.no_grad():
            for i in range(0, len(aligned_faces), self.batch_size):
                if i + self.batch_size < len(aligned_faces):    
                    tmp_embeddings = self.model(aligned_faces[i: i + self.batch_size])
                else:
                    tmp_embeddings = self.model(aligned_faces[i:len(aligned_faces)])

                tmp_embeddings = tmp_embeddings.data

                if face_embeddings is None:
                    face_embeddings = tmp_embeddings
                else:
                    face_embeddings = torch.vstack((face_embeddings, tmp_embeddings))

        return face_embeddings
    
    def postprocess(self, face_embeddings):
        face_embeddings = face_embeddings.cpu().numpy().astype(np.float32)
        face_embeddings = preprocessing.normalize(face_embeddings)
        
        return face_embeddings
    
    def extract(self, images):
        aligned_faces = self.preprocess(images)
        face_embeddings = self.inference(aligned_faces)
        face_embeddings = self.postprocess(face_embeddings)
        return face_embeddings

if __name__ == "__main__":
    pass