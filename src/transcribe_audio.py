import openai
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from faster_whisper import WhisperModel

model_size = "large-v2"
load_dotenv()
# openai.api_key = os.environ.get("OPENAI_API_KEY")


def cut_in_half(filename):
    sound = AudioSegment.from_file(filename)
    halfway_point = len(sound) // 2
    first_half = sound[:halfway_point]
    second_half = sound[halfway_point:]
    name = filename.split(".")[0]
    first_half.export(f"{name}_1.mp3", format="mp3")
    second_half.export(f"{name}_2.mp3", format="mp3")


def write_in_file(data, new_filename, mode="w"):
    with open(new_filename, mode, encoding="utf-8") as new_file:
        new_file.write(data)


def get_transcribe_version(filename):
    f = open(filename, "rb")
    name_of_file = filename.split(".")[0]
    try:
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
        segments, info = model.transcribe(f,  language="ru")
        result = ''.join(list(s.text for s in segments))
        write_in_file(result, f"{name_of_file}.txt")
    except openai.error.APIError as e:
        print(e)
        f.close()
        print("HERE")
        from pydub import AudioSegment
        cut_in_half(filename)
        print("CUT EXECUTED")
        with open(f"{name_of_file}_1.mp3", "rb") as half:
            segments, info = model.transcribe(half,  language="ru")
            result = ''.join(list(s.text for s in segments))
            print("SUCCESS CUT 1")
        write_in_file(result, f"{name_of_file}.txt")
        os.remove(f"{name_of_file}_1.mp3")
        with open(f"{name_of_file}_2.mp3", "rb") as half:
            segments, info = model.transcribe(half,  language="ru")
            result = ''.join(list(s.text for s in segments))
            print("SUCCESS CUT 2")
        write_in_file(result, f"{name_of_file}.txt", mode="a")
        os.remove(f"{name_of_file}_2.mp3")
    f.close()

    return f"{name_of_file}.txt"
