import cv2 as cv
import numpy as np
import face_recognition
import os

from log import get_logger
from effects.filters import (
    RenderedFilter,
    Filter,
)
from effects.effects import (
    needs_more_contrast,
    needs_more_gaussian_noise,
    needs_more_jpeg,
    needs_more_motion_blur,
    needs_more_poisson_noise,
    needs_more_salt_and_pepper_noise,
    needs_more_saturation,
    needs_more_sharpening,
    needs_more_speckle_noise,
)
from effects.utils import (
    needs_more_face_points,
    time_execution,
)

@time_execution
def needs_more_dank(frame,
            filter_list,
            noise_type,
            gauss_amount,
            sp_ratio,
            sp_amount,
            motion,
            sharpening,
            saturation,
            brightness,
            contrast,
            jpeg_iterations,
            jpeg_quality,
            filters_dir,
            overrides,
            effects):
    logger = get_logger()
    filters = []

    for d in os.listdir(filters_dir):
        if os.path.isdir(os.path.join(filters_dir, d)) and d in filter_list:
            f = Filter(os.path.join(filters_dir, d, 'filter.yml'), overrides[d] if d in overrides else {})
            filters.append(f)
            f.describe()

    l = []
    try:
        l = face_recognition.face_landmarks(frame)
    except Exception as exce:
        logger.error("Could not detect faces: {}".format(exce))
    rendered_filters = []
    for face in l:
        face = needs_more_face_points(face)
        for f in [f for f in filters if f.mask]:
            try:
                rendered = f.apply(face, frame)
                if len(rendered) != 0:
                    rendered_filters += rendered
            except Exception as exce:
                logger.error("Could not apply mask {}: {}".format(f.name, exce))

    # Non face filters
    width, height = frame.shape[:2]
    img = {
        "center": (int(height/2),int(width/2)),
    }
    for f in [f for f in filters if not f.mask]:
        try:
            rendered = f.apply(img, frame)
            if len(rendered) != 0:
                rendered_filters += rendered
        except Exception as exce:
            logger.error("Could not apply filter {}: {}".format(f.name, exce))

    rendered_filters = sorted(rendered_filters, key=lambda x: x.priority)
    for f in rendered_filters:
        try:
            frame = f.apply(frame)
        except:
            pass

    for effect in effects:
        if effect == "saturation":
            frame = needs_more_saturation(frame, saturation)
        elif effect == "noise":
            if noise_type == "gauss":
                frame = needs_more_gaussian_noise(frame, gauss_amount)
            elif noise_type == "poisson":
                frame = needs_more_poisson_noise(frame)
            elif noise_type == "speckle":
                frame = needs_more_speckle_noise(frame)
            elif noise_type == "sp":
                frame = needs_more_salt_and_pepper_noise(frame, sp_ratio, sp_amount)
            else:
                logger.error("Unknown noise type {}".format(noise_type))
        elif effect == "sharpening":
            frame = needs_more_sharpening(frame, sharpening)
        elif effect == "contrast":
            frame = needs_more_contrast(frame, brightness, contrast)
        elif effect == "motion":
            frame = needs_more_motion_blur(frame, motion)
        elif effect == "jpeg":
            for i in range(0, jpeg_iterations):
                frame = needs_more_jpeg(frame, jpeg_quality)

    return frame