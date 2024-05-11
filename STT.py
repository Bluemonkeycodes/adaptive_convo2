"""
Notes
----------------------------------------
* I think OpenAI GPT4 has a STT model builtin so this part might not be necessary
*In the future we might be able to load iterable object directly from the mic into STT instead of having a intermediary file
*Shifted it from a streaming model to fixed file model if we want to do above we have to shift back
*returns the list utterences said in the audio file
----------------------------------------
"""
from time import time
from typing import Iterable
from click import echo
from google.cloud import speech
from google.oauth2 import service_account



MIC_SAMPLE_RATE = 16000
SPEECH_TIMEOUT = 5  # seconds

def intialize_client():
    credentials = service_account.Credentials.from_service_account_file('stt-private-key.json')
    client = speech.SpeechClient(credentials=credentials)
    return client

def get_speech_text(
    client: speech.SpeechClient, audio_gen: str, max_alts = 5
) -> list[str]:


    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=MIC_SAMPLE_RATE,
        language_code='en-US',
        max_alternatives=max_alts,
    )

    client = client
    start_time = time()
    with open(audio_gen, "rb") as f:
        content = f.read()
        audio = speech.RecognitionAudio(content=content)
    responses = client.recognize(config=config, audio=audio)
    results = []
    for x in responses.results:
        results.append(x.alternatives[0].transcript)
    return (results)

if __name__ == "__main__":
    client = intialize_client()
    #open file and read bytes
    print(get_speech_text(client, "24-05-09_17-37-17.wav"))