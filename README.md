

## Installation


`pip install git+https://github.com/devzery/devzery_middleware.git`

## Usage

Add the following command to your `settings.py`:

```python
MIDDLEWARE = [
    'devzery_middleware.middleware.RequestResponseLoggingMiddleware',
]

DEVZERY_API_KEY = "YOUR API KEY"
DEVZERY_SOURCE_NAME = "ANY NAME AS YOU WISH, FOR YOU TO IDENTIFY THE SERVICE"
```