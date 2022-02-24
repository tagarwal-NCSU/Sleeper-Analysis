import sys
import os

APP_DIR = "/home/ec2-user/flask_simple/"
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

from app import app as application