import os
from dotenv import load_dotenv
import requests

load_dotenv()
WEBHOOK_LINK = os.getenv("WEBHOOK_LINK")

requests.post(WEBHOOK_LINK, json={"content": "check your wallet"})