import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
from utils.config import AppConfig


class APIClient:
    def __init__(self):
        self.config = AppConfig()

    def handle_request(self, method, url, **kwargs):
        try:
            response = method(url, **kwargs)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"{response.text}"}
        except ConnectionError:
            return {"error": "Connection failed. Please ensure the server is running and accessible."}
        except Timeout:
            return {"error": "The request timed out. Please try again later."}
        except RequestException as e:
            return {"error": f"An unexpected error has occurred: {str(e)}"}

    def predict(self, image_file, location_data):
        files = {"image": ("image.jpg", image_file, "image/jpeg")}
        data = {}

        # Add optional latitude and longitude if provided
        if location_data.get("latitude") is not None:
            data["latitude"] = location_data["latitude"]
        if location_data.get("longitude") is not None:
            data["longitude"] = location_data["longitude"]

        return self.handle_request(
            requests.post,
            self.config.PREDICTION_ENDPOINT,
            files=files,
            data=data
        )

    def submit_feedback(self, prediction_id, original_prediction, user_feedback, user_suggestion):
        data = {
            "id": prediction_id,
            "original_prediction": original_prediction,
            "user_feedback": user_feedback,
            "user_suggestion": user_suggestion
        }

        return self.handle_request(
            requests.post,
            self.config.FEEDBACK_ENDPOINT,
            data=data
        )

    def get_heatmap_data(self, filter_type, **kwargs):
        url = self.config.HEATMAP_ENDPOINT
        params = {}
        if filter_type == "by_days":
            params.update({"days": kwargs.get("days", 30), "page": 1, "per_page": 50})
        elif filter_type == "by_location":
            params.update({
                "latitude": kwargs.get("latitude"),
                "longitude": kwargs.get("longitude"),
                "radius": kwargs.get("radius", 10)
            })
        elif filter_type == "seasonal_clusters":
            params.update({
                "seasonal": kwargs.get("seasonal", 0),
                "clusters": kwargs.get("clusters", 1)
            })
        elif filter_type == "nearby_points":
            params.update({
                "latitude": kwargs.get("latitude"),
                "longitude": kwargs.get("longitude"),
                "radius": kwargs.get("radius", 10),
                "days": kwargs.get("days", 30)
            })

        return self.handle_request(
            requests.get,
            url,
            params=params
        )
