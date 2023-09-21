import openai
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAudio
import os
from dotenv import load_dotenv
import warnings
from pydub import AudioSegment
import pathlib
from src.transcribe_audio import get_transcribe_version
from src.summarizer import make_summarize 
import magic
import logging

from src.tg import help_button, models_buttons

warnings.filterwarnings("ignore")
load_dotenv()

log_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
logging.basicConfig(level=log_level)


openai.api_key = os.environ.get("OPENAI_API_KEY")
telegram_token = os.environ.get('TELEGRAM_TOKEN')
tg_api_id = os.getenv("TG_API_ID")
tg_api_id_hash = os.getenv("TG_API_ID_HASH")


bot = TelegramClient('bot', tg_api_id, tg_api_id_hash).start(bot_token=telegram_token)

file_download_path = "downloaded/"
model_params = {"model": "gpt-3.5-turbo"}
file_formats = ['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg', 'ogg', 'oga', 'flac']
desired_bug_filename = "ISO Media, Apple iTunes ALAC/AAC-LC (.M4A) Audio"
unique_name = None


@bot.on(events.NewMessage(pattern="/help"))
async def send_help(event: events.NewMessage.Event):
    await bot.send_message(event.chat_id, "Доступные команды:\n/config - текущая конфигурация \n"
                                      "/reset_config - переназначение конфига\n"
                                      "Доступные модели: ChatGPT и GPT-4\n"
                          )


@bot.on(events.NewMessage(pattern="/config"))
async def send_configs(event):
    await bot.send_message(event.chat_id, f"Текущая конфигурация:\nМодель:{model_params['model']}\n")


@bot.on(events.NewMessage(pattern='/start'))
async def send_start(event: events.NewMessage.Event):
    await bot.send_message(event.chat_id, 
                           "Скинь мне аудио файл и я сделаю по нему техническое саммари.\n"
                           "<b>Обращаем внимание на использование конфиденциальной информации."
                           "Разрешается использование информации уровня K4.</b>",
                           buttons=[help_button], parse_mode="html")

 
@bot.on(events.NewMessage(pattern="/reset_config"))
async def reset_configs(event):
    await bot.send_message(event.chat_id, 'Выберите тип модели:', buttons=models_buttons)


@bot.on(events.NewMessage(func=lambda e: e.message.message in ["gpt-3.5-turbo", "gpt-4"]))
async def handle_set1(event):
    model_params['model'] = event.message.message
    await bot.send_message(event.chat_id, f'Модель успешно изменена на: {model_params["model"]}')


def create_project_folder():
    pathlib.Path(file_download_path).mkdir(exist_ok=True)


create_project_folder()


def clean_up_specific(file_unique_name, fmt):
    for file in os.listdir(file_download_path):
        if not file.endswith(f".{fmt}") and file.startswith(file_unique_name):
            os.remove(os.path.join(file_download_path, file))


def convert_to_wav(file_path, wav_file_path):
    given_audio = AudioSegment.from_file(file_path, format="m4a")
    given_audio.export(wav_file_path, format="wav")
    return wav_file_path


def transcribe_audio(mp3_audio_path):
    with open(mp3_audio_path, "rb") as f:
        result = openai.Audio.transcribe("whisper-1", file=f, language="ru")
    return result


def clean_up_files(name_to_find):
    for file in os.listdir(file_download_path):
        if file.startswith(name_to_find):
            os.remove(os.path.join(file_download_path, file))


@bot.on(events.NewMessage(func=lambda e: e.message.file))
async def handle_audio(event: events.NewMessage.Event):
    
    try:
        message = event.message
        
        file_info = message.file
        print(file_info)

        secret_user = await event.get_sender()
        print(secret_user)
        
        if secret_user == "nv_27":
            await bot.send_message(message.chat_id, "Привет, Никита, автоматически выставлен gpt-4")
            model_params["model"] = "gpt-4"
        
        unique_name = file_info.name
        print(unique_name)
        file_path = await message.download_media()
        file_extension = file_path.split(".")[-1]
        filepath = f"{file_download_path}/{file_info.id}.{file_extension}"
        new_filepath = f"{file_download_path}/{file_info.id}.wav"
        
        os.rename(file_path, filepath)
        
        ext = magic.from_file(filepath)
        await bot.send_message(message.chat_id, "Транскрибация началась")
        
        if ext == desired_bug_filename:
            convert_to_wav(filepath, new_filepath)
            filename = get_transcribe_version(new_filepath)
        else:
            filename = get_transcribe_version(filepath)
        
        await bot.send_message(message.chat_id, "Транскрибация закончилась")
        clean_up_specific(unique_name, fmt="txt")
        await bot.send_message(message.chat_id, "Начинается суммаризация")
        result = make_summarize(filename, model_params)
        print(result)
        
        try:
            await bot.send_message(message.chat_id, result)
        except Exception as e:
            print(e)
            results = [result[i:i+4096] for i in range(0, len(result), 4096)]
            for res in results:
                await bot.send_message(message.chat_id, res)

    except Exception as e:
        error_message = str(e) + "\n" + "По поводу ошибок пишите @krakenalt или @babais"
        print(e)
        await bot.send_message(message.chat_id, error_message)

    finally:
        if unique_name is not None:
            clean_up_files(unique_name)


bot.run_until_disconnected()
