import torch
import numpy as np
from numpy.typing import NDArray

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

import pathlib

path = pathlib.Path(__file__)
dir_prj = path.parents[3]
dir_ckpts = dir_prj.joinpath("checkpoints/")
dir_cfgs = dir_prj.joinpath("configs/")


PointCoords = list[tuple[int, int]]


class MaskFactory:
    """
    Produces segmentation masks using a pre-trained SAM-2 model given on initialization.
    """

    def __init__(self, model):
        # define the model
        self.model = model
        # create the predictor object
        self.predictor = SAM2ImagePredictor(self.model)


    @classmethod
    def create(cls, ckpt_name_or_path : str, cfg_path : str, device : str = None):
        """
        Craete a MaskFactory instance with a SAM-2 model loaded.

        Args:
            ckpt_name_or_path: Name or full path of the checkpoint file located in `<PROJECTROOT>/checkpoints/` directory
            cfg_path: Path of the config file relative to the SAM-2 root directory, typically starts with `configs/...`

        Returns:
            A new `MaskFactory` instance.
        """
        # set the device if not given
        if not device:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # build SAM-2 model
        is_abs_ckpt = pathlib.Path(ckpt_name_or_path).is_absolute()

        sam2_model = build_sam2(
            ckpt_path=str(dir_ckpts.joinpath(ckpt_name_or_path)) if not is_abs_ckpt else ckpt_name_or_path,
            config_file=cfg_path, # config file path is resolved internally
            device=device
            )
        
        return cls(model=sam2_model)


    def produce(self,
                stream_data : NDArray[np.uint8],
                include_points : PointCoords,
                exclude_points : PointCoords,
                previous_mask : NDArray = None,
                **predict_options
                ) -> NDArray:
        """
        Produces a segmentation mask using given image data.

        TODO better docstring
        """
        prd = self.predictor

        # set image
        prd.set_image(stream_data)

        # concat points
        ndarr_pts = np.concatenate([
            include_points,
            exclude_points
            ]) # [ *include_points, *exclude_points ]

        # define labels
        ndarr_labels = np.concatenate([
            [1] * len(include_points),
            [0] * len(exclude_points)
            ])

        # perform a prediction
        masks, scores, logits = prd.predict(
            point_coords=ndarr_pts,
            point_labels=ndarr_labels,
            mask_input=previous_mask,
            **predict_options # pass options
            )

        """
        
        The outputs are mapped by their first dimension:
            
            masks[i]  = segmentation mask of prediction i
            scores[i] = quality score of prediction i
            logits[i] = raw mask logits of prediction i
        
        """

        # get the max score index
        idx_best = np.argmax(scores)

        # get the max scored mask
        mask_best = masks[idx_best]

        return mask_best
    

"""
TEST
"""
from PIL import Image
import cv2

maskfactory = MaskFactory.create(
    ckpt_name_or_path="sam2.1_hiera_tiny.pt",
    cfg_path="configs/sam2.1/sam2.1_hiera_t.yaml"
    )

include_coords : PointCoords = []
exclude_coords : PointCoords = []
mask_cur : NDArray | None = None

def callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        include_coords.append((x, y))
        
    elif event == cv2.EVENT_RBUTTONDOWN:
        exclude_coords.append((x, y))

    

fimage = Image.open("/home/cbsahmet/Dev/eyebin-clone/datasets/IMG-20260505-WA0137_jpg.rf.84f2adf308c8dcd6a4b37783cfaac18d.jpg")

cv2.namedWindow("TEST-MASKFACTORY")
cv2.setMouseCallback("TEST-MASKFACTORY", callback)

while True:

    image = np.array(fimage)

    view = image
    if mask_cur is not None:
        # Maskeyi görüntüye uygula
        overlay = image.copy()
        overlay[mask_cur] = (0, 255, 0)
        view = cv2.addWeighted(
            image,
            0.6,
            overlay,
            0.4,
            0
        )
    cv2.imshow("TEST-MASKFACTORY", view)
    
    key = cv2.waitKey(500)

    if key == 27: # ESC
        # quit program
        break

    if key == 13: # Enter
        # perform a prediction
        mask_cur = maskfactory.produce(image, include_coords, exclude_coords)
        print(mask_cur.dtype)
        # then clear previous points
        include_coords.clear()
        exclude_coords.clear()