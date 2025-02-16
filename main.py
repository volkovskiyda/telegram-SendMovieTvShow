import os, ffmpeg, json
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application
from asyncio import run

load_dotenv()

def main():
    token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    name = os.getenv('NAME')
    base_url = os.getenv('BASE_URL') or 'http://localhost:8081/bot'
    timeout = os.getenv('READ_TIMEOUT') or 30
    should_convert = os.getenv('SHOULD_CONVERT')
    if should_convert: should_convert = json.loads(should_convert.lower())
    else: should_convert = True

    application = (
        Application.builder()
        .token(token)
        .base_url(base_url)
        .read_timeout(float(timeout))
        .build()
    )
    bot = application.bot

    video_folder = single_directory(dir = '/data')
    if not video_folder: return
    if should_convert:
        converted_folder = converted(video_folder)
        convert(video_folder, converted_folder)
        print("convert_to_folder done: ", os.listdir(converted_folder))
    else:
        converted_folder = video_folder

    run(
        send_video(
            bot=bot,
            chat_id=chat_id,
            text=name or os.path.basename(video_folder),
            converted_folder=converted_folder
        )
    )
    print("send video done")

def single_directory(dir: str) -> str:
    path = os.path.join(dir)
    listdir = os.listdir(path)
    if len(listdir) == 1: return os.path.join(path, listdir[0])
    else: print("Directories: ", os.listdir(path))

def converted(video_folder: str) -> str:
    converted = 'converted'
    os.makedirs(os.path.join(video_folder, converted), exist_ok=True)
    return os.path.join(video_folder, converted)

def convert(video_folder: str, converted_folder: str):
    for file in os.listdir(video_folder):
        if file.endswith('.avi') or file.endswith('.mkv'):
            print("File: ", file)
            input_file = os.path.join(video_folder, file)
            output_file = os.path.join(converted_folder, file.rsplit('.', 1)[0] + '.mp4')
            ffmpeg.input(input_file).output(output_file, codec='copy', format='mp4', loglevel='quiet').run()

async def send_video(bot: Bot, chat_id: str, text: str, converted_folder: str):
    await bot.send_message(
        chat_id=chat_id,
        text = text,
        disable_notification=True,
    )
    for file in sorted(os.listdir(converted_folder)):
        await bot.send_video(
            chat_id=chat_id,
            caption=file,
            video=os.path.join(converted_folder, file),
            filename=file,
            disable_notification=True,
        )

if __name__ == "__main__":
    main()
