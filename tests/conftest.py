import pytest
import os
import sys

# Add the parent directory to PYTHONPATH so we can import api_sniper
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
