"""Setup script for react-ai-agent package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="react-ai-agent",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A general-purpose AI Agent using the ReAct pattern",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/react-ai-agent",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langgraph>=0.0.20",
        "langsmith>=0.1.0",
        "tiktoken>=0.5.0",
        "mcp>=0.1.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
)
