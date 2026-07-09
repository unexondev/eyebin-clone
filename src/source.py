from roboflow import Roboflow
from roboflow import Project

rf = Roboflow(api_key="B97j25nsHBqLzY4Mi3rP")
project = rf.workspace("enders-workspace-bl73b").project("eyebin")

version_1 = project.version(1)
dataset_v1 = version.download("yolov8")

from roboflow import Roboflow
rf = Roboflow(api_key="B97j25nsHBqLzY4Mi3rP")
project = rf.workspace("enders-workspace-bl73b").project("eyebin")
version = project.version(2)
dataset_v2 = version.download("yolov8")