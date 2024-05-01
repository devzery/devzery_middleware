import json
import time
import requests
from urllib.parse import parse_qs
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class RequestResponseLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.api_endpoint = "http://localhost:8081/api"
        self.api_key = settings.DEVZERY_API_KEY
        self.source_name = settings.DEVZERY_SOURCE_NAME

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):

        elapsed_time = time.time() - request.start_time
        headers = {key: value for key, value in request.META.items() if key.startswith('HTTP_') or key in ['CONTENT_LENGTH', 'CONTENT_TYPE']}

        if request.content_type == 'application/json':
            body = json.loads(request.body) if request.body else None
        elif request.content_type.startswith('multipart/form-data') or request.content_type.startswith(
                'application/x-www-form-urlencoded'):
            body = parse_qs(request.body.decode('utf-8'))
        else:
            body = None

        data = {
            'request': {
                'method': request.method,
                'path': request.get_full_path(),
                'headers': headers,
                'body': body,
            },
            'response': {
                'status_code': response.status_code,
                'content': response.content.decode('utf-8'),
            },
            'elapsed_time': elapsed_time,
        }

        # Log the captured data (you can customize this part)
        # print(json.dumps(data, indent=4))

        # if self.api_endpoint:
        try:
            if self.api_key and self.source_name :
                headers = {'Authorization': f'Bearer {self.api_key}', 'Source_Name': self.source_name}
                response1 = requests.post(self.api_endpoint, json=data, headers=headers)
                if response1.status_code != 200:
                    print(f"Failed to send data to API endpoint. Status code: {response1.status_code}")
            else:
                print("Devzery: No API Key or Source given!")
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while sending data to API endpoint: {e}")

        return response

