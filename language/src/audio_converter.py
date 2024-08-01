import tempfile
from io import BytesIO
import subprocess
from typing import Optional
from urllib.parse import urlparse
import os
import aiofiles
import aiofiles.os
import httpx
from pydub import AudioSegment


def _is_url(string) -> bool:
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_filename_from_url(url):
    # Parse the URL to get the path
    parsed_url = urlparse(url)
    path = parsed_url.path

    # Extract the filename from the path
    filename = os.path.basename(path)
    return filename


def _get_file_extension(file_name_or_url) -> str:
    if file_name_or_url.startswith("http://") or file_name_or_url.startswith(
        "https://"
    ):
        file_name = get_filename_from_url(file_name_or_url)
    else:
        file_name = file_name_or_url

    _, extension = os.path.splitext(file_name)
    return extension[1:]


def convert_to_wav(source_url_or_file: str, source_type: Optional[str] = None) -> bytes:
    if not source_type:
        source_type = _get_file_extension(source_url_or_file)

    if _is_url(source_url_or_file):
        local_file = tempfile.NamedTemporaryFile(suffix=source_type)
        response = httpx.get(source_url_or_file)
        local_file.write(response.content)
        local_file.seek(0)
        local_filename = local_file.name
    else:
        local_filename = source_url_or_file

    given_audio = AudioSegment.from_file(
        local_filename, format=source_type
    )  # run ffmpeg directly using a thread pool
    given_audio = given_audio.set_frame_rate(16000)
    given_audio = given_audio.set_channels(1)

    wav_file = BytesIO()
    given_audio.export(wav_file, format="wav", codec="pcm_s16le")

    return wav_file.getvalue()


async def convert_to_wav_with_ffmpeg(
    source_url_or_file: str, source_type: Optional[str] = None
) -> bytes:
    local_file = None
    if not source_type:
        source_type = _get_file_extension(source_url_or_file)

    if _is_url(source_url_or_file):
        local_file = tempfile.NamedTemporaryFile(suffix="." + source_type)
        response = httpx.get(source_url_or_file)
        local_file.write(response.content)
        local_file.seek(0)
        local_filename = local_file.name
    else:
        local_filename = source_url_or_file

    wav_filename = os.path.basename(os.path.splitext(local_filename)[0] + ".wav")
    command = (
        f"ffmpeg -i {local_filename}"
        f" -acodec pcm_s16le -ar 16000 -ac 1 {wav_filename}"
    )
    subprocess.run(
        command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    async with aiofiles.open(wav_filename, "rb") as wav_file:
        audio_data = await wav_file.read()

    await aiofiles.os.remove(wav_filename)
    if local_file:
        local_file.close()

    return audio_data


def convert_wav_bytes_to_mp3_bytes(wav_bytes: bytes) -> bytes:
    wav_file = BytesIO(wav_bytes)
    wav_audio = AudioSegment.from_file(wav_file, format="wav")
    wav_audio = wav_audio.set_frame_rate(44100)
    mp3_file = BytesIO()
    wav_audio.export(mp3_file, format="mp3")
    return mp3_file.getvalue()
