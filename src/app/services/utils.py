import torch
import torch.backends.cudnn as cudnn
import numpy as np
import cv2
import base64
from skimage import transform as trans

def get_device(request_device='cpu', default_id=0):
    if request_device[:3] != 'cpu':
        tokens = request_device.split(":")
        device_id = default_id if len(tokens) == 1 else int(tokens[1])

        if torch.cuda.is_available():
            if torch.cuda.device_count() > device_id:
                return f"cuda:{device_id}"
            else:
                return f"cuda:{default_id}"

    return 'cpu'

def check_keys(model, pretrained_state_dict):
    ckpt_keys = set(pretrained_state_dict.keys())
    try:
        model_keys = set(model.state_dict().keys())
        used_pretrained_keys = model_keys & ckpt_keys
        unused_pretrained_keys = ckpt_keys - model_keys
        missing_keys = model_keys - ckpt_keys
        print('Missing keys:{}'.format(len(missing_keys)))
        print('Unused checkpoint keys:{}'.format(len(unused_pretrained_keys)))
        print('Used keys:{}'.format(len(used_pretrained_keys)))
        assert len(used_pretrained_keys) > 0, 'load NONE from pretrained checkpoint'
        return True
    except:
        pass

def remove_prefix(state_dict, prefix):
    ''' Old style model is stored with all names of parameters sharing common prefix 'module.' '''
    print('remove prefix \'{}\''.format(prefix))
    f = lambda x: x.split(prefix, 1)[-1] if x.startswith(prefix) else x
    return {f(key): value for key, value in state_dict.items()}

def load_model(model, pretrained_path, device):
    print('Loading pretrained model from {}'.format(pretrained_path))
    if 'cpu' in device:
        pretrained_dict = torch.load(pretrained_path, map_location=lambda storage, loc: storage)
    else:
        pretrained_dict = torch.load(pretrained_path, map_location=lambda storage, loc: storage.cuda(device))
    if "state_dict" in pretrained_dict.keys():
        pretrained_dict = remove_prefix(pretrained_dict['state_dict'], 'module.')
    else:
        pretrained_dict = remove_prefix(pretrained_dict, 'module.')
    check_keys(model, pretrained_dict)
    model.load_state_dict(pretrained_dict, strict=False)
    return model

def resize_img(img, input_size):
    img_copy = img.copy()
    if len(img_copy) == 3:
        padded_img = np.ones((input_size[0], input_size[1], 3), dtype = np.uint8) * 114
    else:
        padded_img = np.ones(input_size, dtype = np.uint8) * 114
    
    r = min(input_size[0] / img_copy.shape[0], input_size[1] / img_copy.shape[1])
    resized_img = cv2.resize(img_copy, (int(img_copy.shape[1] * r), int(img_copy.shape[0] * r)))
    padded_img[: int(img_copy.shape[0] * r), : int(img_copy.shape[1] * r)] = resized_img
    return padded_img, r

def convert_for_inference(img):
    img = np.float32(img)
    img -= (104, 117, 123)
    img = img.transpose(2, 0, 1) # channel, heigth, width
    img = torch.from_numpy(img).unsqueeze(0)
    return img

def get_max_by_area(dets, landms):
    compute_area = lambda box: (box[2] - box[0]) * (box[3] - box[1])
    areas = [compute_area[box] for box in dets]
    max_idx = np.argmax(areas)

    return dets[max_idx], landms[max_idx], areas[max_idx]

def decode_bs64(img_bs64):
    img_bytes = base64.decode(img_bs64)                                                         # im_bytes is a binary image
    img_arr = np.frombuffer(img_bytes, dtype = np.uint8)                                        # im_arr is one-dim Numpy array
    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    return img