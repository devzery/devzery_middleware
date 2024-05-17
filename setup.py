from setuptools import setup

setup(
    name='devzery_middleware',
    version='0.0.3',
    description='SDK for capturing API requests and responses in Django',
    author='Devzery',
    author_email='your@email.com',
    packages=['devzery_middleware'],
    install_requires=[
        'Django>=3.0.0',
        'requests>=2.0.0'
    ],
)