import torch
import numpy as np
from numpy.typing import NDArray

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

import pathlib

path = pathlib.Path(__file__)
dir_prj = path.parents[2]
dir_ckpts = dir_prj.joinpath("checkpoints/")
dir_cfgs = dir_prj.joinpath("configs/")


class SegmentationEngine:

    def __init__(self, model):
        # define the model
        self.model = model
        # create the predictor object
        self.predictor = SAM2ImagePredictor(self.model)


    @classmethod
    def create(cls, ckpt_name_or_path : str, cfg_path : str, device : str = None):
        """
        Craete a SegmentationEngine instance with a SAM-2 model loaded.

        Args:
            ckpt_name_or_path: Name or full path of the checkpoint file located in `<PROJECTROOT>/checkpoints/` directory
            cfg_name: Path of the config file relative to the SAM-2 root directory, typically starts with `configs/...`


        Returns:
            A new `SegmentationEngine` instance.
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


    def process(self, stream_data : NDArray[np.uint8]):
        pass


"""
TEST
"""
seng = SegmentationEngine.create(
    ckpt_name_or_path="sam2.1_hiera_tiny.pt",
    cfg_path="configs/sam2.1/sam2.1_hiera_t.yaml"
    )

print(seng.model)