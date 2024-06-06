"""
Notes: 
----------------------------------------
* Right now the function takes in the filename, this could change depending on structure of final code
* Outputs to a specified file as a .wav file
* Google Key file is explicitly written, this should be changed
* Doesn't return path to file, this could be changed depending on final code
"""


from google.cloud import texttospeech
from google.oauth2 import service_account

def intialize_client():
    credentials = service_account.Credentials.from_service_account_file('tts-private-key.json')
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    return client

def text_to_speech(client, text : str, filename : str) -> str:
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name = "en-US-Journey-F", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    try:
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open(filename, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio content written to file "{filename}"')
    except Exception as e:
        print(e)
    

if __name__ == "__main__":
    client = intialize_client()
    text_to_speech(client, "Sup gang how's it hanging?", "output.wav")
