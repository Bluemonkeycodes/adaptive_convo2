from audiorecorder import * 
from STT import get_speech_text, intialize_client as stt_intialize_client
from TTS import text_to_speech, intialize_client as tts_intialize_client
from openai import OpenAI
import playsound
import os
from dotenv import load_dotenv
load_dotenv()

"""
Notes
--------------------------
install pip install playsound==1.2.2
latest version of playsound is not working
make sure to remove key from openai before pushing to git
"""
print("Recording audio...")
path = MicRecorder().record(3)
print("Stopped Recording")
print("Converting audio to text...")
stt_client = stt_intialize_client()
STTresponse = get_speech_text(stt_client, path)
os.remove(path)
print(f"You said: {STTresponse[0]}")
print("Asking OpenAI for a response...")
key = os.getenv("OPENAI_API_KEY")
openAIclient = OpenAI(api_key= key)

gptResponse = openAIclient.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful voice assistant."},
        {"role": "user", "content": STTresponse[0]},
    ],
    max_tokens=75
).choices[0].message.content
print(f"OpenAI Response: {gptResponse}")
print("Converting text to speech...")
tts_client = tts_intialize_client()
text_to_speech(tts_client, gptResponse, "output.wav")
playsound.playsound("output.wav")

