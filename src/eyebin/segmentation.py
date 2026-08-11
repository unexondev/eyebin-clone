import torch


def get_sam2_model(pt_path):
    # select the device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # build the model
    sam2_model = build_sam2(CONFIG, CHECKPOINT, device=device)



class SegmentationEngine:


    def __init__(self):
        pass


    @classmethod
    def create(cls, pt_path : str):

        device = "cuda" if torch.cuda.is_available() else "cpu"

        sam2_model = build_sam2(CONFIG, CHECKPOINT, device=device)