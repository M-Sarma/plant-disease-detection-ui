import requests

from src.config import AppConfig


class APIClient:
    def __init__(self):
        self.config = AppConfig()

    def predict(self, image_file, location_data):
        files = {"image": ("image.jpg", image_file, "image/jpeg")}
        data = {}

        # Add optional latitude and longitude if provided
        if location_data.get("latitude") is not None:
            data["latitude"] = location_data["latitude"]
        if location_data.get("longitude") is not None:
            data["longitude"] = location_data["longitude"]

        # Do not set Content-Type; requests handles it
        response = requests.post(
            self.config.PREDICTION_ENDPOINT,
            files=files,
            data=data
        )
        return response.json() if response.status_code == 200 else response.text

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
