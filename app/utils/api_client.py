import requests
from app.utils.config import AppConfig


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

        response = requests.post(
            self.config.PREDICTION_ENDPOINT,
            files=files,
            data=data
        )
        return response.json() if response.status_code == 200 else response.text

    def submit_feedback(self, prediction_id, original_prediction, user_feedback, user_suggestion):
        """
        Submit feedback for a prediction

        Args:
            prediction_id (str): The unique identifier of the prediction
            original_prediction (dict): The original prediction data
            user_feedback (str): User feedback (e.g. 'positive' or 'negative')
            user_suggestion (str): User suggested class/category

        Returns:
            dict: Response data if successful, otherwise error text
        """
        data = {
            "id": prediction_id,
            "original_prediction": original_prediction,
            "user_feedback": user_feedback,
            "user_suggestion": user_suggestion
        }

        response = requests.post(
            self.config.FEEDBACK_ENDPOINT,
            data=data
        )
        return response.json() if response.status_code == 201 else response.text

    def get_heatmap_data(self, filter_type, **kwargs):
        """
        Fetch heatmap data based on the filter type and parameters.

        Args:
            filter_type (str): Type of filter ('days', 'location', 'seasonal_clusters', 'nearby').
            kwargs: Additional parameters for the API call.

        Returns:
            dict: Heatmap data if successful, otherwise error text.
        """
        url = self.config.HEATMAP_ENDPOINT
        params = {}

        if filter_type == "days":
            params.update({"days": kwargs.get("days", 30), "page": 1, "per_page": 50})
        elif filter_type == "location":
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
        elif filter_type == "nearby":
            params.update({
                "latitude": kwargs.get("latitude"),
                "longitude": kwargs.get("longitude"),
                "radius": kwargs.get("radius", 10),
                "days": kwargs.get("days", 30)
            })

        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else response.text
