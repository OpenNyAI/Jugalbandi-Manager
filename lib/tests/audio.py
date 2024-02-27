from unittest import TestCase
from audio_converter import convert_wav_bytes_to_mp3_bytes
import subprocess

class TestAudio(TestCase):

    def test_mp3_convertor(self):
        wav_file_path = './tests/'
        with open(wav_file_path + 'test.wav', 'rb') as f:
            wav_bytes = f.read()
        mp3_bytes = convert_wav_bytes_to_mp3_bytes(wav_bytes)
        with open(wav_file_path + 'test.mp3', 'wb') as f:
            f.write(mp3_bytes)
        command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', wav_file_path + 'test.mp3']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        print(result.stderr)