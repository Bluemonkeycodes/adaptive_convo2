"""
Notes
----------------------------------------
----------------------------------------
"""

import pyaudio
from google.cloud import speech
from google.oauth2 import service_account
import time
import threading
import queue

# Audio recording parameters
RATE = 16000
CHUNK_DIVISION = 10
CHUNK = int(RATE / CHUNK_DIVISION)  # 100ms


def initialize_client():
    credentials = service_account.Credentials.from_service_account_file('stt-private-key.json')
    client = speech.SpeechClient(credentials=credentials)
    return client

def response_handler(responses, response_queue):
    try:
        for response in responses:
            response_queue.put(response)
    except Exception as e:
        pass

def STT(SILENCE_THRESHOLD = 2, MAX_TIME = 30) -> str:
    """Returns the transcript of the audio file.
        SILENCE_THRESHOLD: The time in seconds after which the STT stops listening if there is no new words detected.
        MAX_TIME: The maximum time in seconds for which the STT will listen to the audio file, will cut off no matter situation after this.
    
    """
    client = initialize_client()

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
    response_queue = queue.Queue()
    response_thread = threading.Thread(target=response_handler, args=(responses, response_queue))
    response_thread.start()

    started = False
    starttime = time.time()
    endtime = time.time()
    transcript = ""

    try:
        while True:
            if (time.time() - starttime) > MAX_TIME:
                break
            try:
                response = response_queue.get(timeout=SILENCE_THRESHOLD)
            except queue.Empty:
                if started and ((time.time() - endtime) > SILENCE_THRESHOLD) and transcript:
                    break
                continue

            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            endtime = time.time()
            if result.is_final:
                started = True
                endtime = time.time()
                transcript += result.alternatives[0].transcript
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        audio_interface.terminate()
        response_thread.join()
        print("Stopped listening")
        return transcript

if __name__ == "__main__":
    print(STT(2,10))
