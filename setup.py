#!/usr/bin/env python3
"""
Setup script for Rhylthyme CLI Runner
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Rhylthyme CLI Runner - Command-line interface for running and validating Rhylthyme programs"

setup(
    name="rhylthyme-cli-runner",
    version="0.1.1-alpha",
    description="CLI runner for Rhylthyme real-time program schedules",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Rhylthyme Team",
    author_email="team@rhylthyme.org",
    url="https://github.com/rhylthyme/rhylthyme-cli-runner",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "jsonschema>=4.0.0",
        "pyyaml>=6.0",
        "colorama>=0.4.0",
        "rhylthyme-spec>=0.1.0-alpha",
    ],
    extras_require={
        "dev": [
            # Testing framework
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "pytest-mock>=3.0.0",
            "pytest-xdist>=2.0.0",  # Parallel test execution
            
            # Code quality
            "black>=21.0.0",
            "flake8>=3.8.0",
            "isort>=5.0.0",
            
            # Type checking
            "mypy>=0.800",
            
            # Testing utilities
            "responses>=0.12.0",  # Mock HTTP responses
            "freezegun>=1.0.0",   # Mock datetime
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "build": [
            "build>=0.7.0",
            "twine>=3.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rhylthyme=rhylthyme_cli_runner.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    keywords="real-time, scheduling, logistics, cli, validation",
    project_urls={
        "Bug Reports": "https://github.com/rhylthyme/rhylthyme-cli-runner/issues",
        "Source": "https://github.com/rhylthyme/rhylthyme-cli-runner",
        "Documentation": "https://github.com/rhylthyme/rhylthyme-cli-runner#readme",
    },
) 