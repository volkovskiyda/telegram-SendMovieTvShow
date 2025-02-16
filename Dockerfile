FROM python

RUN mkdir project data
VOLUME /data

WORKDIR /project
COPY main.py requirements.txt /project/

RUN apt update && apt install -y ffmpeg
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python main.py
