import os
import sys

# Add application directory to Python path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, app_dir)