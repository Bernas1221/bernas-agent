"""
Setup script para BERNAS-AGENT no Render.com
"""

from setuptools import setup, find_packages

setup(
    name="bernas-agent",
    version="1.0.0",
    description="Bot de Economia Autônoma entre IAs",
    author="Carlos",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "bernas-agent=app:main",
        ],
    },
    python_requires=">=3.11",
)