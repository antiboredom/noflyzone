export GOOGLE_APPLICATION_CREDENTIALS="text-to-speech-key.json"

rm recordings/*.wav

source venv/bin/activate

python generate.py

for f in recordings/*.wav
do
  sox "$f" "$f.effect.wav" reverb 10 sinc 400-5005
done
