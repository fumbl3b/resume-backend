from flask import Flask
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize extensions
cors = CORS()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))