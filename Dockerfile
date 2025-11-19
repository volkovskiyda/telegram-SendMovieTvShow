FROM python

RUN mkdir project data converted
VOLUME /data
VOLUME /converted

WORKDIR /project
COPY main.py /project/

RUN apt update && apt install -y ffmpeg
RUN python -m pip install --upgrade pip
RUN pip install -U python-dotenv python-telegram-bot ffmpeg-python asyncio

CMD ["python", "main.py"]
