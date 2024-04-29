from locust import HttpUser, task, between

class StreamlitAppUser(HttpUser):
    # Define host for the Streamlit app, if it'll change
    host = "http://localhost:8501"
    wait_time = between(1, 5)

    @task
    def load_streamlit_app(self):
        # Load the Streamlit app main page
        self.client.get("/")

class TriviaAPIUser(HttpUser):
    host = "https://opentdb.com"
    wait_time = between(5, 6)

    @task
    def fetch_questions(self):
        params = {
            'amount': 5,
            'type': 'boolean'
        }
        # Send a GET request to the Trivia API
        self.client.get("/api.php", params=params)
