import requests
from config import AppConfig

class APIClient:
    def __init__(self):
        self.config = AppConfig()

    def predict(self, image_file, location_data):
        files = {"file": ("image.jpg", image_file, "image/jpeg")}
        data = {
            "latitude": location_data["latitude"],
            "longitude": location_data["longitude"]
        }
        
        response = requests.post(
            self.config.PREDICTION_ENDPOINT,
            files=files,
            data=data,
            headers=self.config.multipart_headers
        )
        return response.json() if response.status_code == 200 else None

    def get_heatmap_data(self, filters):
        response = requests.get(
            self.config.HEATMAP_ENDPOINT,
            params=filters,
            headers=self.config.headers
        )
        return response.json() if response.status_code == 200 else None

    def get_metrics(self):
        response = requests.get(
            self.config.METRICS_ENDPOINT,
            headers=self.config.headers
        )
        return response.json() if response.status_code == 200 else None
