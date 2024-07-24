import os
import urllib.request
from dotenv import load_dotenv
from celery import shared_task

@shared_task
def text_to_speech(text):
    load_dotenv()
    client_id = os.getenv("CLOVA_CLIENT_ID")
    client_secret = os.getenv("CLOVA_CLIENT_SECRET")
    encText = urllib.parse.quote(text)
    data = f"speaker=nminsang&volume=0&speed=0&pitch=0&format=mp3&text={encText}"
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request_obj = urllib.request.Request(url)
    request_obj.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request_obj.add_header("X-NCP-APIGW-API-KEY", client_secret)
    response = urllib.request.urlopen(request_obj, data=data.encode('utf-8'))
    rescode = response.getcode()

    if rescode == 200:
        return response.read(), None
    else:
        return None, rescode


