from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sentinelops",
    version="0.1.0",
    author="SentinelOps Team",
    author_email="info@sentinelops.com",
    description="Full observability for AI/LLM systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sentinelops/sentinelops",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opentelemetry-api>=1.12.0",
        "opentelemetry-sdk>=1.12.0",
        "opentelemetry-exporter-otlp>=1.12.0",
        "kafka-python>=2.0.2",
        "requests>=2.28.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.5.0"],
        "huggingface": ["transformers>=4.30.0", "huggingface-hub>=0.16.0"],
        "tokenizers": ["tiktoken>=0.4.0", "transformers>=4.30.0"],
        "aws": ["boto3>=1.26.0"],
        "gcp": ["google-cloud-aiplatform>=1.25.0"],
        "azure": ["azure-identity>=1.12.0", "azure-ai-ml>=1.4.0"],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.5.0",
            "transformers>=4.30.0",
            "huggingface-hub>=0.16.0",
            "tiktoken>=0.4.0",
            "boto3>=1.26.0",
            "google-cloud-aiplatform>=1.25.0",
            "azure-identity>=1.12.0",
            "azure-ai-ml>=1.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sentinelops=sentinelops.cli:main",
        ],
    },
)