from roboflow import Project
from roboflow.core.dataset import Dataset

class RFDatasetManager:
    def __init__(self, project : Project):
        self.project = project
        self._datasets : dict[int, dict[str, Dataset]] = {}
        self._version = None

    def switch_version(self, version : int):
        self._version = version

    def download_dataset(self, model_format : str, **kwargs):
        version = self._version
        if version is None:
            raise RuntimeError("version is not specified, please use switch_version() before downloading a dataset")
        
        ver = self.project.version(version)

        dataset = None
        try:
            dataset = ver.download(model_format, **kwargs)
        except RuntimeError:
            # that means API call returned a failed object
            raise RuntimeError("Roboflow API call failed returning response body: ")
        self._datasets.setdefault(version, {})[model_format] = dataset

    def get(self, version : int, ):
        pass

datasets = {
    "v1": version.download("yolov8")

}