import time
import threading
import sys
import signal
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pycaw.utils import AudioDeviceState
from PIL import Image
import pystray
import os
import keyboard


HEADPHONES_KEYWORD = "name heapdphpne"
OWNER_TAG = "tag" #можно закоментитьs

def get_default_audio_device():
    try:
        CoInitialize()
    except:
        pass
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    finally:
        try:
            CoUninitialize()
        except:
            pass

def set_mute(mute: bool):
    try:
        interface = get_default_audio_device()
        interface.SetMute(mute, None)
    except Exception as e:
        print(f"Ошибка установки mute: {e}")

def set_volume(volume: float):
    try:
        interface = get_default_audio_device()
        interface.SetMasterVolumeLevelScalar(volume, None)
    except Exception as e:
        print(f"Ошибка установки громкости: {e}")

def check_audio_device():
    for device in AudioUtilities.GetAllDevices():
        if device.state == AudioDeviceState.Active:
            name = device.FriendlyName.lower()
            if HEADPHONES_KEYWORD in name and OWNER_TAG in name: #Здесь тоже
                return device.FriendlyName
    return None

def monitor():
    CoInitialize()
    current_device = None
    try:
        while True:
            connected_device = check_audio_device()
            if connected_device != current_device:
                if connected_device:
                    set_mute(False)
                    set_volume(1.0)
                    print(f"{OWNER_TAG}: '{connected_device}' подключены — звук включен.")
                else:
                    set_mute(True)
                    print(f"{OWNER_TAG}: Наушники отключены — звук выключен.")
                current_device = connected_device
            time.sleep(2)
    finally:
        CoUninitialize()

def toggle_mute():
    print("Переключение звука")
    device = get_default_audio_device()
    current = device.GetMute()
    device.SetMute(0 if current else 1, None)

def volume_up():
    print("Увеличение громкости")
    device = get_default_audio_device()
    current_volume = device.GetMasterVolumeLevelScalar()
    device.SetMasterVolumeLevelScalar(min(1.0, current_volume + 0.05), None)

def volume_down():
    print("Уменьшение громкости")
    device = get_default_audio_device()
    current_volume = device.GetMasterVolumeLevelScalar()
    device.SetMasterVolumeLevelScalar(max(0.0, current_volume - 0.05), None)

def hotkeys():
    keyboard.add_hotkey('ctrl+m', toggle_mute)
    keyboard.add_hotkey('ctrl+up', volume_up)
    keyboard.add_hotkey('ctrl+down', volume_down)
    keyboard.add_hotkey('ctrl+q', exit_app)
    keyboard.wait()

def on_quit(icon, item=None):
    icon.stop()
    sys.exit()

def exit_app():
    on_quit(icon)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def main():
    global icon

    signal.signal(signal.SIGINT, lambda sig, frame: on_quit(icon))
    signal.signal(signal.SIGTERM, lambda sig, frame: on_quit(icon))

    threading.Thread(target=monitor, daemon=True).start()
    threading.Thread(target=hotkeys, daemon=True).start()

    image = Image.open(resource_path("icon.ico"))
    icon = pystray.Icon("AudioController", image, "AudioController",
                        menu=pystray.Menu(pystray.MenuItem('Выход', on_quit)))
    icon.run()

if __name__ == "__main__":
    main()