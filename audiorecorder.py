"""
Notes
----------------------------------------
* MicRecorder.record(seconds) starts recording audio from the microphone for the specified number of seconds 
and creates a file with name following "%y-%m-%d_%H-%M-%S".wav format and returns path

----------------------------------------
"""
import queue
from datetime import datetime
from os.path import join
from threading import Event
from typing import Callable, Iterable
import sounddevice
from click import echo
from soundfile import SoundFile
from typing import Callable
from pynput import mouse


MIC_SAMPLE_RATE = 16000


class KeyInput:
    def __init__(self, action: Callable) -> None:
        self._action = action
        self._listener = mouse.Listener(on_click=self._on_click)

    def monitor_key(self) -> None:
        self._listener.start()
        print("Started Listening")

    def _on_click(self, _x, _y, _button, pressed) -> None:
        if pressed:
            self._listener.stop()
            self._action()
            print("Stopped Listening")
        return False

class AudioWriter:
    """Write audio data to sound file"""

    def __init__(self, output_path: str, sample_rate: int | None = None) -> None:
        self._sample_rate = sample_rate or int(
            sounddevice.query_devices(kind="input")["default_samplerate"]
        )

        if not output_path.endswith(".wav"):
            output_path += ".wav"

        self._soundfile = SoundFile(
            output_path, mode="x", samplerate=self._sample_rate, channels=1
        )

    def __enter__(self) -> SoundFile:
        return self._soundfile

    def __exit__(self, _type, _value, _traceback) -> None:
        self._soundfile.close()


class MicReader:
    """Get input from microphone"""

    def __init__(self, seconds: int, mic_rec_callback: Callable | None = None) -> None:
        self._mic_rec_callback = mic_rec_callback
        self._mic_queue = queue.SimpleQueue()
        self._stop_event = Event()
        self.starttime = datetime.now()
        self.seconds = seconds + 1

    def mic_audio_gen(self, wait_key: bool = False) -> Iterable[bytes]:
        if wait_key:
            echo("Click to continue")
            KeyInput(self.close).monitor_key()
        stream = sounddevice.InputStream(
            channels=1,
            samplerate=MIC_SAMPLE_RATE,
            callback=self._audio_callback,
            dtype="int16",
        )

        with stream:
            while True:
                chunk = self._mic_queue.get()

                if not chunk:
                    break

                yield chunk

    def close(self) -> None:
        self._stop_event.set()

    def _audio_callback(self, indata, _frames, _time, status) -> None:
        """This is called (from a separate thread) for each audio block."""


        if self._stop_event.is_set():
            self._mic_queue.put(None)
        if (datetime.now() - self.starttime).seconds >= self.seconds:
            self.close()
        else:
            self._mic_queue.put(indata.tobytes())
            if self._mic_rec_callback:
                try:
                    self._mic_rec_callback(indata)
                except RuntimeError:
                    print("Warning: writing audio runtime error")


class MicRecorder:
    rec_dir = "./"
    rec_filename = datetime.now().strftime("%y-%m-%d_%H-%M-%S")
    _stop_flag = False

    @staticmethod
    def record(seconds : int) -> None:
        MicRecorder._stop_flag = False
        rec_path = join(MicRecorder.rec_dir, MicRecorder.rec_filename + ".wav")

        with AudioWriter(rec_path, sample_rate=MIC_SAMPLE_RATE) as audio_writer:
            mic_reader = MicReader(mic_rec_callback=audio_writer.write, seconds=seconds)
            mic_input_gen = mic_reader.mic_audio_gen()
            for _ in mic_input_gen:
                if MicRecorder._stop_flag is True:
                    break


            mic_reader.close()
            return rec_path

    @staticmethod
    def stop():
        MicRecorder._stop_flag = True

if __name__ == "__main__":
    print(MicRecorder().record(3))
