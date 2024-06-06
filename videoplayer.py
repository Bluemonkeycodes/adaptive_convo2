import vlc
import threading

def play_video(filepath: str) -> None:
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(filepath)
    player.set_media(media)

    media_end_event = threading.Event()

    # sets flag ending program
    def end_callback(event):
        print("Media finished playing")
        media_end_event.set()

    events = player.event_manager()
    events.event_attach(vlc.EventType.MediaPlayerEndReached, end_callback)

    player.play()

    media_end_event.wait()

def play_video_threading(filepath: str) -> None:
    playback_thread = threading.Thread(target=play_video, args=(filepath,))
    playback_thread.start()

if __name__ == "__main__":
    play_video_threading("01_episode.mp4")