from setuptools import setup, find_packages

setup(
    name="sum_service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "grpcio==1.60.0",
        "grpcio-tools==1.60.0",
        "grpcio-health-checking==1.60.0",
        "grpcio-reflection==1.60.0",
        "websockets==12.0",
    ],
    python_requires=">=3.9",
    author="Your Name",
    description="A gRPC and WebSocket service for calculating sums",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
) 