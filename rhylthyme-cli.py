#!/usr/bin/env python3
"""
Rhylthyme CLI Runner

This script provides a convenient way to run the Rhylthyme CLI
without installing the package.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from rhylthyme.cli import main

if __name__ == "__main__":
    main() 