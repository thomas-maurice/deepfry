import numpy as np
import cv2 as cv
from log import get_logger
import time

def get_barycenter(points):
    arr = np.asarray(points)
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return (int(sum_x/length), int(sum_y/length))

def get_face_dimension(face):
    mouth = face['center_mouth']
    reye = face['center_right_eye']
    leye = face['center_left_eye']
    midbrow = face['center_midbrow']

    eye_distance = np.floor(np.sqrt(pow(leye[0] - reye[0], 2) + pow(leye[1] - reye[1], 2))) * 2
    face_height  = np.floor(np.sqrt(pow(mouth[0] - midbrow[0], 2) + pow(mouth[1] - midbrow[1], 2))) * 2.1

    return (int(eye_distance), int(face_height))

def needs_more_face_points(face):
    face['center_mouth'] = get_barycenter(face['top_lip'] + face['bottom_lip'])
    face['center_right_eye'] = get_barycenter(face['right_eye'])
    face['center_left_eye'] = get_barycenter(face['left_eye'])
    face['center_nose_tip'] = get_barycenter(face['nose_tip'])
    face['center_nose_bridge'] = get_barycenter(face['nose_bridge'])
    face['center_midbrow'] = get_barycenter([face['center_right_eye'], face['center_left_eye']])
    face['center_chin'] = get_barycenter(face['chin'])
    face['center_nose'] = get_barycenter([face['center_nose_tip'], face['center_nose_bridge']])
    slope = (face['center_chin'][0] - face['center_midbrow'][0], face['center_chin'][1] - face['center_midbrow'][1])
    face['rotation'] = np.rad2deg(np.arctan2(slope[1], slope[0]))
    return face

def downsize_image(frame, max_height, max_width):
    height, width = frame.shape[:2]
    hdiff, wdiff = (height - max_height, width - max_width)
    if hdiff <= 0 and wdiff <= 0:
        # All good no need to downsample
        return frame

    if hdiff > wdiff:
        # hdiff is bigger, this means we have to scale according to
        # the height to have the max dimension respected.
        ratio = max_height / height
        return cv.resize(frame, (int(width*ratio), int(height*ratio)))
    else:
        ratio = max_width / width
        return cv.resize(frame, (int(width*ratio), int(height*ratio)))

def time_execution(func):
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start = time.time()
        ret = func(*args, **kwargs)
        end = time.time()
        diff = end-start
        logger.info("Function {} ran in {}s".format(func.__name__, diff))
        return ret

    return wrapper