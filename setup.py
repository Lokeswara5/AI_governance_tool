from setuptools import setup, find_packages

setup(
    name="ai-governance-tool",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.5.0",
        "reportlab>=3.6.8",
        "numpy>=1.21.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
    author="Lokeswara5",
    author_email="your.email@example.com",
    description="An ISO 42001 compliance checker for AI governance policies",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Lokeswara5/AI_governance_tool",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ai-governance-check=ai_governance_tool.cli:main",
        ],
    },
)