# Setup file for Meerkatics Python SDK

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="meerkatics",
    version="1.0.0",
    author="Meerkatics Team",
    author_email="support@meerkatics.com",
    description="Superior AI monitoring and observability for LLM applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meerkatics/meerkatics",
    project_urls={
        "Bug Tracker": "https://github.com/meerkatics/meerkatics/issues",
        "Documentation": "https://docs.meerkatics.com",
        "Homepage": "https://meerkatics.com",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.8.0",
            "google-generativeai>=0.3.0",
            "boto3>=1.28.0",
            "cohere>=4.0.0",
            "sentence-transformers>=2.2.0",
            "langchain>=0.1.0",
            "llama-index>=0.9.0",
            "streamlit>=1.28.0",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.8.0"],
        "google": ["google-generativeai>=0.3.0"],
        "aws": ["boto3>=1.28.0"],
        "cohere": ["cohere>=4.0.0"],
        "langchain": ["langchain>=0.1.0"],
        "llamaindex": ["llama-index>=0.9.0"],
        "streamlit": ["streamlit>=1.28.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "meerkatics=meerkatics.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
