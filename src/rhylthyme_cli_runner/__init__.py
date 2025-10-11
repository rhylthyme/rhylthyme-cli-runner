#!/usr/bin/env python3
"""
Rhylthyme CLI Runner Package

This package provides the command-line interface for running and validating
Rhylthyme real-time program schedules.
"""

__version__ = "0.1.0-alpha"
__author__ = "Rhylthyme Team"
__description__ = "CLI runner for Rhylthyme real-time program schedules"

from .cli import cli, main

__all__ = ["cli", "main"]
