import cv2 as cv
import numpy as np
import cv2 as cv
import face_recognition
import sys
import random
import json
import copy
import yaml
import logging
import requests
from tabulate import tabulate
import tempfile
import os

from log import get_logger
from effects.utils import (
    get_face_dimension,
)

class RenderedFilter(object):
    def __init__(self, frame, x1, y1, x2, y2, alpha_s, alpha_l, priority):
        self.frame = frame
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.priority = priority
        self.alpha_s = alpha_s
        self.alpha_l = alpha_l
        self.logger = get_logger()

    def apply(self, image):
        cp = copy.deepcopy(image)
        for c in range(0, 3):
            cp[self.y1:self.y2, self.x1:self.x2, c] = (self.alpha_s * self.frame[:, :, c] +
                    self.alpha_l * cp[self.y1:self.y2, self.x1:self.x2, c])

        return cp

class Filter():
    def __init__(self, config_name, overrides = {}):
        self.config_name = config_name
        self.overrides = overrides
        self.logger = get_logger()
        self.logger.debug("Loading filter {}".format(config_name))
        # Load the shit out of it
        with open(config_name, 'r') as stream:
            config = yaml.load(stream)['filter']
            self.name = self.config_or_override_or_default(
                "name",
                config,
                overrides,
                "unnamed",
            )
            self.file_name = self.config_or_override_or_default(
                "file_name",
                config,
                overrides,
                "unnamed",
            )
            self.image = cv.imread(self.file_name, -1)
            self.xcenter = self.config_or_override_or_default(
                "xcenter",
                config,
                overrides,
                0,
            )
            self.ycenter = self.config_or_override_or_default(
                "ycenter",
                config,
                overrides,
                0,
            )
            self.scale = self.config_or_override_or_default(
                "scale",
                config,
                overrides,
                1,
            )
            self.height = self.image.shape[1]
            self.width = self.image.shape[0]
            self.applies = self.config_or_override_or_default(
                "applies",
                config,
                overrides,
                [],
            )
            self.rotate = self.config_or_override_or_default(
                "rotate",
                config,
                overrides,
                False,
            )
            self.mask = self.config_or_override_or_default(
                "mask",
                config,
                overrides,
                True,
            )
            self.angle = self.config_or_override_or_default(
                "angle",
                config,
                overrides,
                0,
            )
            self.priority = self.config_or_override_or_default(
                "priority",
                config,
                overrides,
                0,
            )
            self.description = self.config_or_override_or_default(
                "description",
                config,
                overrides,
                "No description provided",
            )

    def config_or_override_or_default(self, k, c, o, d):
        if k in o:
            return o[k]
        elif k in c:
            return c[k]
        else:
            return d


    def describe(self):
        self.logger.info("""Filter {}:
    - config: {}
    - filename: {}
    - width: {}
    - height: {}
    - xcenter: {}
    - ycenter: {}
    - applies: {}
    - overrides: {}
    - mask: {}
""".format(
            self.name,
            self.config_name,
            self.file_name,
            self.width,
            self.height,
            self.xcenter,
            self.ycenter,
            self.applies,
            self.overrides,
            self.mask,
        ))

    def compute_mask_multiplier(self, face):
        fheight, fwidth = get_face_dimension(face)
        xscale = (fwidth * self.scale) / self.width
        yscale = (fheight * self.scale) / self.height
        return (xscale + yscale) / 2

    def apply(self, face, frame):
        multiplier = 1
        if self.mask:
            multiplier = self.compute_mask_multiplier(face)
        else:
            x, y = frame.shape[:2]
            xscale = (x * self.scale) / self.width
            yscale = (y * self.scale) / self.height
            multiplier = (xscale + yscale) / 2

        rendered = []
        for name, coordinates in face.items():
            if name in self.applies:
                self.logger.info("Applying filter {}".format(self.name))
                x_offset, y_offset = coordinates

                resized_filter = cv.resize(
                    self.image,
                    (0, 0),
                    fx=multiplier,
                    fy=multiplier,
                )

                # applies the base rotation
                if self.angle != 0:
                    image_center = tuple(np.array(resized_filter.shape[1::-1]) / 2)
                    rot_mat = cv.getRotationMatrix2D(image_center, 90-self.angle, 1.0)
                    resized_filter = cv.warpAffine(resized_filter, rot_mat, resized_filter.shape[1::-1], flags=cv.INTER_LINEAR)

                # rotate it now
                if self.rotate:
                    image_center = tuple(np.array(resized_filter.shape[1::-1]) / 2)
                    rot_mat = cv.getRotationMatrix2D(image_center, 90-face['rotation'], 1.0)
                    resized_filter = cv.warpAffine(resized_filter, rot_mat, resized_filter.shape[1::-1], flags=cv.INTER_LINEAR)

                x_offset = int(
                    x_offset - resized_filter.shape[0] - self.xcenter * multiplier
                )

                y_offset = int(
                    y_offset - resized_filter.shape[1] - self.ycenter * multiplier
                )

                y1, y2 = y_offset, y_offset + resized_filter.shape[0]
                x1, x2 = x_offset, x_offset + resized_filter.shape[1]

                # Apply various corrections in case we go out of bounds
                if y1 < 0:
                    diff = -y1
                    y1 = 0
                    resized_filter = resized_filter[diff:, :]

                if x1 < 0:
                    diff = -x1
                    x1 = 0
                    resized_filter = resized_filter[:, diff:]

                if y2 > frame.shape[0]:
                    diff = y2 - frame.shape[0]
                    y2 = frame.shape[0]-1
                    resized_filter = resized_filter[:-diff-1, :]

                if x2 > frame.shape[1]:
                    diff = x2 - frame.shape[1]
                    x2 = frame.shape[1]-1
                    resized_filter = resized_filter[:, :-diff-1]

                self.logger.info("Frame size   : {}, {}".format(frame.shape[1], frame.shape[0]))
                self.logger.info("y2           : {}, {}".format(x2, y2))
                self.logger.info("Mask size    : {}, {}".format(resized_filter.shape[1], resized_filter.shape[0]))
                self.logger.info("x2           : {}, {}".format(x2-x1, y2-y1))

                alpha_s = resized_filter[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s

                rs = RenderedFilter(
                    x1 = x1,
                    x2 = x2,
                    y1 = y1,
                    y2 = y2,
                    alpha_l = alpha_l,
                    alpha_s = alpha_s,
                    priority = self.priority,
                    frame = resized_filter,
                )

                rendered.append(rs)

        return rendered