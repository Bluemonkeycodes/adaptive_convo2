"""
Notes
----------------------------------------
* I think OpenAI GPT4 has a STT model builtin so this part might not be necessary
*In the future we might be able to load iterable object directly from the mic into STT instead of having a intermediary file
*Shifted it from a streaming model to fixed file model if we want to do above we have to shift back
*returns the list utterences said in the audio file
----------------------------------------
"""

import pyaudio
from google.cloud import speech
from google.cloud import speech
from google.oauth2 import service_account

# Audio recording parameters
RATE = 16000
CHUNK_DIVISON = 10 #Bigger number means faster cut off time for end of speech
CHUNK = int(RATE / CHUNK_DIVISON)  # 100ms

def intialize_client():
    credentials = service_account.Credentials.from_service_account_file('stt-private-key.json')
    client = speech.SpeechClient(credentials=credentials)
    return client


def STT() -> str:
    client = intialize_client()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

    audio_interface = pyaudio.PyAudio()
    audio_stream = audio_interface.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=None
    )
    print("Listening...")

    audio_generator = (audio_stream.read(CHUNK) for _ in iter(int, 1))

    requests = (speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator)

    responses = client.streaming_recognize(streaming_config, requests)

    try:
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            if result.is_final:
                transcript = result.alternatives[0].transcript
                print(f"You said: {transcript}")
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        audio_interface.terminate()
        print("Stopped listening")
        return transcript

if __name__ == "__main__":
    STT()