import threading
import requests
import json
import time
from urllib.parse import parse_qs
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.api_endpoint = getattr(settings, 'DEVZERY_URL', "https://server-v3-7qxc7hlaka-uc.a.run.app/api/add")
        # self.api_endpoint = settings.DEVZERY_URL if settings.DEVZERY_URL else "https://server-v3-7qxc7hlaka-uc.a.run.app/api/add"
        self.api_key = settings.DEVZERY_API_KEY
        self.source_name = settings.DEVZERY_SERVER_NAME

        print(self.api_endpoint)

    def process_request(self, request):
        request.start_time = time.time()
        request._body = request.body

    def send_data_to_api_sync(self, data, response_content):
        try:
            if (self.api_key and self.source_name) and (response_content is not None):
                headers = {
                    'x-access-token': self.api_key,
                    'source-name': self.source_name
                }
                response1 = requests.post(self.api_endpoint, json=data, headers=headers)
                if response1.status_code == 200:
                    response1.json()['message']
                    print("Devzery: Success!", response1.json()['message'])
                if response1.status_code != 200:
                    print(f"Failed to send data to API endpoint. Status code: {response1.status_code}")
            elif (self.api_key and self.source_name) is None:
                print("Devzery: No API Key or Source given!")
            else:
                print("Devzery: Response content is not JSON, not adding")
        except requests.RequestException as e:
            print(f"Error occurred while sending data to API endpoint: {e}")

    def process_response(self, request, response):
        try:
            if (self.api_key and self.source_name):
                elapsed_time = time.time() - request.start_time
                headers = {key: value for key, value in request.META.items() if
                           key.startswith('HTTP_') or key in ['CONTENT_LENGTH', 'CONTENT_TYPE']}

                if request.content_type == 'application/json':
                    body = json.loads(request._body) if request._body else None

                elif request.content_type.startswith('multipart/form-data') or request.content_type.startswith(
                        'application/x-www-form-urlencoded'):
                    body = parse_qs(request._body.decode('utf-8'))

                else:
                    body = None

                try:
                    response_content = response.content.decode('utf-8')
                    json.loads(response_content)
                except:
                    response_content = None

                data = {
                    'request': {
                        'method': request.method,
                        'path': request.get_full_path(),
                        'headers': headers,
                        'body': body,
                    },
                    'response': {
                        'status_code': response.status_code,
                        'content': response_content
                    },
                    'elapsed_time': elapsed_time,
                }

                threading.Thread(target=self.send_data_to_api_sync, args=(data, response_content)).start()

                return response

            else:
                if self.api_key:
                    print("Devzery: No Source Name")
                elif self.source_name:
                    print("Devzery: No API KEY")
                return response

        except Exception as e:

            print(f"Devzery: Error occurred Capturing: {e}")
            return response
