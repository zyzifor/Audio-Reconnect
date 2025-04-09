from pycaw.pycaw import AudioUtilities

devices = AudioUtilities.GetAllDevices()
for device in devices:
    print(f"Name: {device.FriendlyName}, State: {device.state}")
