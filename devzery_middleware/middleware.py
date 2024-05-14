import asyncio
import json
import time
import aiohttp
from urllib.parse import parse_qs
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class RequestResponseLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.api_endpoint = settings.DEVZERY_URL if settings.DEVZERY_URL else "https://server-v3-7qxc7hlaka-uc.a.run.app/api/add"
        self.api_key = settings.DEVZERY_API_KEY
        self.source_name = settings.DEVZERY_SOURCE_NAME

    def process_request(self, request):
        request.start_time = time.time()

    async def send_data_to_api(self, data, response_content):
        try:
            if (self.api_key and self.source_name) and (response_content is not None):
                headers = {
                    'x-access-token': self.api_key,
                    'source-name': self.source_name
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.api_endpoint, json=data, headers=headers) as response1:
                        if response1.status != 200:
                            print(f"Failed to send data to API endpoint. Status code: {response1.status}")
            elif (self.api_key and self.source_name):
                print("Devzery: No API Key or Source given!")
        except aiohttp.ClientError as e:
            print(f"Error occurred while sending data to API endpoint: {e}")

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

        asyncio.ensure_future(self.send_data_to_api(data, response_content))

        return response

