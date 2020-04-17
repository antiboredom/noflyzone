YOUTUBE_URL="rtmp://a.rtmp.youtube.com/live2"
KEY=""

ffmpeg \
  -re -loop 1 -i bg.jpg \
  -stream_loop -1 \
  -i audiotrack.wav -c:a aac \
  -s 1280x720 -ab 128k \
  -vcodec libx264 -pix_fmt yuv420p \
  -maxrate 2048k -bufsize 2048k \
  -preset ultrafast \
  -framerate 30 \
  -g 2 -strict experimental \
  -f flv "$YOUTUBE_URL/$KEY" &
