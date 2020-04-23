export GOOGLE_APPLICATION_CREDENTIALS="text-to-speech-key.json"
YOUTUBE_URL="rtmp://a.rtmp.youtube.com/live2"
TWITCH_URL="rtmp://live-jfk.twitch.tv/app/"
KEY=""

# make sure recordings exists
mkdir -p recordings

# make sure data exists
mkdir -p data

# remove old recordings
rm recordings/*.wav

# activate virtualenv if necessary
if [ "x$VIRTUAL_ENV" == "x" ] ; then
    source venv/bin/activate
fi

# create new recordings
python generate.py

# apply reverb and "megaphone" effect
for f in recordings/*.mp3
do
    # convert to wav
    ffmpeg -i "$f" -acodec pcm_u8 -ar 22050 "$f.wav"
    sox "$f.wav" "$f.effect.wav" reverb 10 sinc 400-5005
done

# stitch recordings together
rm concatlist.txt
for f in recordings/*.effect.wav
do
  echo "file '$f'" >> concatlist.txt
done

ffmpeg -y -f concat -safe 0 -i concatlist.txt -c copy audiotrack.wav

# ffmpeg -y -f lavfi -i color=c=black:s=1280x720:r=5 -i audiotrack.wav -crf 0 -shortest live.mp4

# kill previous stream
pkill -9 ffmpeg

# start new stream
# ffmpeg \
#   -re -loop 1 -i bg.jpg \
#   -stream_loop -1 \
#   -i audiotrack.wav -c:a aac \
#   -s 1280x720 -ab 128k \
#   -vcodec libx264 -pix_fmt yuv420p \
#   -maxrate 2048k -bufsize 2048k \
#   -preset ultrafast \
#   -framerate 30 \
#   -g 2 -strict experimental \
#   -f flv "$TWITCH_URL/$KEY" &
