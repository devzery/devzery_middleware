import json
import time
import requests
from django.utils.deprecation import MiddlewareMixin

class RequestResponseLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.api_endpoint = "http://localhost:8081/api"

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):

        elapsed_time = time.time() - request.start_time

        data = {
            'request': {
                'method': request.method,
                'path': request.get_full_path(),
                'headers': dict(request.headers),
                'body': json.loads(request.body) if request.body else None,
            },
            'response': {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.content.decode('utf-8'),
            },
            'elapsed_time': elapsed_time,
        }

        # Log the captured data (you can customize this part)
        print(json.dumps(data, indent=4))

        if self.api_endpoint:
            try:
                response = requests.post(self.api_endpoint, json=data)
                if response.status_code != 200:
                    print(f"Failed to send data to API endpoint. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while sending data to API endpoint: {e}")

        return response