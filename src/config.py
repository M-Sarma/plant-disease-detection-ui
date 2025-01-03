import os

class AppConfig:
    def __init__(self):
        self.API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
        self.PREDICTION_ENDPOINT = f"{self.API_BASE_URL}/api/predict"
        self.FEEDBACK_ENDPOINT = f"{self.API_BASE_URL}/api/feedback"
        self.HEATMAP_ENDPOINT = f"{self.API_BASE_URL}/api/heatmap"
        self.METRICS_ENDPOINT = f"{self.API_BASE_URL}/api/metrics"

    @property
    def headers(self):
        return {
            'Content-Type': 'application/json'
        }
    @property
    def multipart_headers(self):
        return {
            'Content-Type': 'multipart/form-data'
        }
