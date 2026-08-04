## Send Movie / TV Show to Telegram

### **Description:**
Sends a folder of movie or TV show video files to a Telegram chat. Files are converted to `mp4`
with `ffmpeg` when needed, then uploaded one by one with duration and resolution metadata attached,
so Telegram shows them as playable videos rather than documents.

Point it at a directory containing a single subfolder of videos, and it sends every episode in
sorted order. Failed uploads are retried three times, and errors are reported to `DEVELOPER_ID`.

### **Conversion rules:**
- `.avi` and `.mkv` files are converted to `.mp4`; anything already `.mp4` is sent as is
- files under 2000 MB are remuxed with `codec=copy` (fast, no quality loss)
- files over 2000 MB drop extra streams, or fully re-encode to `libx264` / `aac` when `CONVERT_CODEC=true`

### **Configuration:**
Copy `.env.example` to `.env` and fill it in:

| Variable | Description |
| --- | --- |
| `BOT_TOKEN` | Telegram bot token |
| `CHAT_ID` | target chat to send the videos to |
| `DEVELOPER_ID` | chat to report errors and completion to (optional) |
| `NAME` | caption sent before the batch; defaults to the folder name |
| `BASE_URL` | Bot API endpoint, default `http://localhost:8081/bot` |
| `READ_TIMEOUT` | upload read timeout in seconds, default `30` |
| `START_INDEX` | 1-based index of the first file to send, default `1` |
| `END_INDEX` | index of the last file to send, `0` means all |
| `CONVERT_CODEC` | re-encode large files instead of dropping streams, default `false` |
| `BASE_PATH` | root containing `data/` and `converted/`, default `.` |

> Uploads larger than 50 MB require a [local Bot API server](https://github.com/volkovskiyda/docker-telegram-bot-api).
> `BASE_URL` points at it by default.

### **Run with Docker:**
```bash
docker run --rm --env-file .env \
  -v /path/to/videos:/data \
  -v /path/to/converted:/converted \
  ghcr.io/volkovskiyda/sendmovietvshowbot
```

`/data` must contain exactly one subfolder — the show or movie to send. Converted files are written
to `/converted` and reused on the next run.

### **Run locally:**
```bash
pip install -U python-dotenv python-telegram-bot ffmpeg-python asyncio
python main.py
```

Requires `ffmpeg` on `PATH`.
