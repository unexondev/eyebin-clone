"""
Example SAM2 runtime training script
"""

import cv2
import numpy as np
import torch

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor


"""
For checkpoint file directories
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"
DATASET_DIR = PROJECT_ROOT / "datasets"
"""
---------------------------------
"""

CHECKPOINT = "checkpoints/sam2.1_hiera_tiny.pt"
CONFIG = "configs/sam2.1/sam2.1_hiera_l.yaml"

image = cv2.imread("image.jpg")
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

device = "cuda" if torch.cuda.is_available() else "cpu"

sam2_model = build_sam2(CONFIG, CHECKPOINT, device=device)
predictor = SAM2ImagePredictor(sam2_model)

# Görüntünün embedding'ini bir kere hesapla
predictor.set_image(image_rgb)

points = []


def mouse_callback(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])

        point_coords = np.array(points)
        point_labels = np.ones(len(points), dtype=np.int32)

        masks, scores, logits = predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            multimask_output=True,
        )

        # En yüksek skorlu maskeyi seç
        best_idx = np.argmax(scores)
        mask = masks[best_idx]

        # Maskeyi görüntüye uygula
        overlay = image.copy()
        overlay[mask] = (0, 255, 0)

        result = cv2.addWeighted(
            image,
            0.6,
            overlay,
            0.4,
            0
        )

        # Tıklanan noktaları göster
        for px, py in points:
            cv2.circle(result, (px, py), 5, (0, 0, 255), -1)

        cv2.imshow("SAM 2", result)


cv2.namedWindow("SAM 2")
cv2.setMouseCallback("SAM 2", mouse_callback)

cv2.imshow("SAM 2", image)

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC
        break

    if key == ord("r"):
        points.clear()
        cv2.imshow("SAM 2", image)

cv2.destroyAllWindows()