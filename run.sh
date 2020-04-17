export GOOGLE_APPLICATION_CREDENTIALS="text-to-speech-key.json"

# remove old recordings
rm recordings/*.wav

source venv/bin/activate

# create new recordings
python generate.py

# apply reverb and "megaphone" effect
for f in recordings/*.wav
do
  sox "$f" "$f.effect.wav" reverb 10 sinc 400-5005
done

# stitch together
rm concatlist.txt
for f in recordings/*.effect.wav
do
  echo "file '$f'" >> concatlist.txt
done

ffmpeg -y -f concat -safe 0 -i concatlist.txt -c copy audiotrack.wav

# ffmpeg -y -f lavfi -i color=c=black:s=1280x720:r=5 -i audiotrack.wav -crf 0 -shortest live.mp4

pkill -9 ffmpeg

./stream.sh
