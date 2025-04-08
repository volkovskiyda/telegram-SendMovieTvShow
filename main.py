import os, ffmpeg, json
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application
from asyncio import run

load_dotenv()

developer_id = os.getenv('DEVELOPER_ID')
base_path = os.getenv('BASE_PATH') or '/'

def main():
    token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    name = os.getenv('NAME')
    base_url = os.getenv('BASE_URL') or 'http://localhost:8081/bot'
    timeout = os.getenv('READ_TIMEOUT') or 30
    start_index = int(os.getenv('START_INDEX') or 1) - 1
    end_index = int(os.getenv('END_INDEX') or 0)
    if end_index == 0: end_index = None

    application = (
        Application.builder()
        .token(token)
        .base_url(base_url)
        .read_timeout(float(timeout))
        .build()
    )
    bot = application.bot

    video_folder = single_directory(dir = f'{base_path}/data')
    if not video_folder: return
    should_convert = len([f for f in os.listdir(video_folder) if not f.endswith('.mp4')]) > 0
    if should_convert:
        converted_folder = os.path.join(f'{base_path}/converted')
        convert(video_folder, converted_folder)
        print("convert_to_folder done: ", os.listdir(converted_folder))
    else:
        converted_folder = video_folder

    run(
        send_all_videos(
            bot=bot,
            chat_id=chat_id,
            text=name or os.path.basename(video_folder),
            converted_folder=converted_folder,
            start_index=start_index,
            end_index=end_index,
        )
    )
    print("send video done")

def single_directory(dir: str) -> str:
    listdir = [f for f in os.listdir(dir) if not os.path.isfile(f)]
    if len(listdir) == 1: return os.path.join(dir, listdir[0])
    else: print("Directories: ", listdir)

def convert(video_folder: str, converted_folder: str):
    for file in [file for file in os.listdir(video_folder) if file.endswith('.avi') or file.endswith('.mkv')]:
        input_file = os.path.join(video_folder, file)
        output_file = os.path.join(converted_folder, file.rsplit('.', 1)[0] + '.mp4')
        vid = ffmpeg.input(input_file)
        if os.path.getsize(input_file) >> 20 > 2000:
            vid.filter('scale', -1, 720).output(output_file, map='0:a:0', format='mp4', loglevel='quiet').run()
        else:
            vid.output(output_file, codec='copy', format='mp4').run()

async def send_all_videos(bot: Bot, chat_id: str, text: str, converted_folder: str, start_index: int, end_index: int):
    files = sorted([file for file in os.listdir(converted_folder) if file.endswith('.mp4')])[start_index:end_index]

    if len(files) > 1: await bot.send_message(chat_id=chat_id, text = text, disable_notification=True)
    for file in files:
        await retry(
            target=send_video,
            target_args=(bot, chat_id, file, os.path.join(converted_folder, file)),
            error_target=send_message_developer,
            error_target_args=(bot, f"Error sending file: {file}"),
            retries=3,
        )
    await send_message_developer(bot, f"Files sent: {text} ({converted_folder})")

async def send_video(bot: Bot, chat_id: str, file: str, video: str): 
    probe = ffmpeg.probe(video)
    try:
        duration = int(float(probe['format']['duration']))
    except:
        duration = None
    try:
        width = int(probe['streams'][0]['width'])
        height = int(probe['streams'][0]['height'])
    except:
        width = None
        height = None
    print(f"Sending video: {file} ({video}), duration: {duration}, width: {width}, height: {height}")
    await bot.send_video(
        chat_id=chat_id,
        caption=file,
        video=video,
        filename=file,
        duration=duration,
        width=width,
        height=height,
        disable_notification=True
    )

async def send_message_developer(bot: Bot, text: str):
    if developer_id: await bot.send_message(chat_id=developer_id, text=text, disable_notification=True)

async def retry(
    target = None, target_args = (),
    error_target = None, error_target_args = (),
    retries = 3,
):
    for i in range(retries):
        try:
            await target(*target_args)
            break
        except Exception as e:
            print(f"Error: {e}")
            if i == retries - 1:
                if error_target: await error_target(*error_target_args)
                raise e

if __name__ == "__main__":
    main()
