from roboflow import Roboflow

rf = Roboflow(api_key="B97j25nsHBqLzY4Mi3rP")
project = rf.workspace("enders-workspace-bl73b").project("eyebin")
version = project.version(1)
dataset = version.download("yolov8")

