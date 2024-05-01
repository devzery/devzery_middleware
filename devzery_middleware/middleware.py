import json
import time
from django.utils.deprecation import MiddlewareMixin

class RequestResponseLoggingMiddleware(MiddlewareMixin):
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

        return response