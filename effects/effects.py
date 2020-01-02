import cv2 as cv
import numpy as np
import random

def needs_more_jpeg(frame, level):
    _, enc = cv.imencode('.jpg',frame, [cv.IMWRITE_JPEG_QUALITY, level])
    return cv.imdecode(enc, 1)

def needs_more_saturation(frame, saturation):
    frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV).astype("float32")
    (h, s, v) = cv.split(frame)
    s = np.round(s*saturation)
    s = np.clip(s,0,255)
    frame = cv.merge([h,s,v])
    return cv.cvtColor(frame.astype("uint8"), cv.COLOR_HSV2BGR)

def needs_more_contrast(frame, brightness=10, contrast=50):
    return cv.addWeighted(frame, 1. + contrast/127., frame, 0, brightness-contrast)

def needs_more_sharpening(frame, factor):
    kernel = np.zeros( (9,9), np.float32)
    kernel[4,4] = 2.0
    boxFilter = np.ones( (9,9), np.float32) / factor
    kernel = kernel - boxFilter
    return cv.filter2D(frame, -1, kernel)

def needs_more_gaussian_noise(image, var):
    row,col,ch= image.shape
    mean = 0
    sigma = var**0.5
    gauss = np.random.normal(mean,sigma,(row,col,ch))
    gauss = gauss.reshape(row,col,ch)
    noisy = image + gauss
    return noisy

def needs_more_poisson_noise(image):
    vals = len(np.unique(image))
    vals = 2 ** np.ceil(np.log2(vals))
    noisy = np.random.poisson(image * vals) / float(vals)
    return noisy

def needs_more_speckle_noise(image):
    row,col,ch = image.shape
    gauss = np.random.randn(row,col,ch)
    gauss = gauss.reshape(row,col,ch)
    noisy = image + image * gauss
    return noisy

def needs_more_salt_and_pepper_noise(image, s_vs_p, amount):
    row,col,ch = image.shape
    out = np.copy(image)
    # Salt mode
    num_salt = np.ceil(amount * image.size * s_vs_p)
    coords = [np.random.randint(0, i - 1, int(num_salt))
              for i in image.shape]
    out[tuple(coords)] = 1

    # Pepper mode
    num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
    coords = [np.random.randint(0, i - 1, int(num_pepper))
        for i in image.shape]

    out[tuple(coords)] = 0
    return out

def needs_more_motion_blur(frame, size):
    if size == 0:
        return frame
    kernel_motion_blur = np.zeros((size, size))
    kernel_motion_blur[int((size-1)/2), :] = np.ones(size)
    kernel_motion_blur = kernel_motion_blur / size
    return cv.filter2D(frame, -1, kernel_motion_blur)