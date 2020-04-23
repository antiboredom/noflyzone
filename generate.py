import re
import time
import json
from subprocess import call
import random
from glob import glob
from requests_html import HTMLSession
import requests
from pydub import AudioSegment

# from google.cloud import texttospeech
# import mstextexample
# client = texttospeech.TextToSpeechClient()

HIDE_DATE = True

with open("text-to-speech-key.json", "r") as infile:
    KEYS = json.load(infile)


def get_data():
    session = HTMLSession()
    r = session.get(
        "https://www.iatatravelcentre.com/international-travel-document-news/1580226297.htm"
    )

    content = r.html.find(".middle", first=True).text

    data_filename = time.strftime("%Y-%m-%d-%H-%M") + ".txt"
    with open("data/" + data_filename, "w") as outfile:
        outfile.write(content)

    content = content.replace("–", "-")

    content = re.sub("\n{2,}", "\n\n", content)

    content = re.sub("\(.*?\)", " ", content)

    items = re.split("\n\n", content)

    items = [i for i in items if re.search("[A-Z]+ - published", i)]

    content = content.replace(" (COVID-19)", "")

    content = content.replace(" COVID-19", "covid nineteen")

    if HIDE_DATE:
        items = [re.sub(" - published .*", "", i) for i in items]

    items = [i.split("\n") for i in items]

    items = [(i[0], "\n".join(i[1:])) for i in items]

    return items


def post_audio(src, dest):
    if dest is None:
        dest = src + ".effect.wav"

    args = [src, dest, "reverb", "10", "sinc", "400-5005"]
    call(args)
    return dest


def synthesize_google(text, outname):
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    voice = texttospeech.types.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C",
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=1.0,
    )

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    with open(outname, "wb") as out:
        out.write(response.audio_content)


def synthesize_local(text, outname):
    call(["say", "-o", outname, text])
    return outname


def synthesize_ms(text, outname):
    token_url = "https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
    headers = {"Ocp-Apim-Subscription-Key": KEYS["ms_key"]}
    response = requests.post(token_url, headers=headers)
    access_token = str(response.text)

    url = "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
        "User-Agent": "YOUR_RESOURCE_NAME",
    }

    voice_name = "en-US-AriaNeural"
    style = "empathetic"
    body = """
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{}">
                 <prosody rate="-6.00%">
                    <mstts:express-as style="{}">
                        {}
                    </mstts:express-as>
                </prosody>
            </voice>
        </speak>
    """.format(
        voice_name, style, text
    )

    response = requests.post(url, headers=headers, data=body)

    if response.status_code == 200:
        with open(outname, "wb") as audio:
            audio.write(response.content)
    else:
        print("Error status code: {}".format(response.status_code))
        print("Reason: {}".format(response.reason))

    return outname


def add_effects():
    print("adding effects")
    for f in glob("recordings/*.wav"):
        if "effect" in f or "mixed" in f:
            continue
        call(["sox", f, f + ".effect.wav", "reverb", "10", "sinc", "400-5005"])

        # call(["sox", f, "silence.flac", f + ".effect.flac", "reverb", "10", "sinc", "400-5005"])
        call(
            [
                "ffmpeg",
                "-y",
                "-i",
                "bell.mp3",
                "-i",
                f + ".effect.wav",
                "-vn",
                "-filter_complex",
                "acrossfade=d=0.4:c1=tri:c2=tri",
                f + ".mixed.wav",
            ]
        )


def stitch2():
    files = glob("recordings/*.mixed.wav")
    random.shuffle(files)

    out = []
    for f in files:
        out.append(f)
        out.append("silence.wav")

    out = ["file '{}'".format(f) for f in out]
    print(out)

    with open("concatlist.txt", "w") as outfile:
        outfile.write("\n".join(out))

    args = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "concatlist.txt",
        "-c",
        "copy",
        "fg.wav",
    ]
    call(args)

    bgs = glob("bg_audio/*.wav")

    overlay_args = [
        "ffmpeg",
        "-y",
        "-i",
        "fg.wav",
        "-i",
        random.choice(bgs),
        "-filter_complex",
        "amix=inputs=2:duration=shortest",
        "docs/radio.mp3",
    ]

    call(overlay_args)


def generate_bgs():
    for f in glob("bg_audio/*.mp3"):
        bg_sound = AudioSegment.from_mp3(f)
        bg_dur = 4 * 60 * 60 * 1000  # 4 hours
        bg_track = AudioSegment.empty()
        while len(bg_track) < bg_dur:
            crossfade = 5000

            if len(bg_track) == 0:
                crossfade = 0

            bg_track = bg_track.append(bg_sound, crossfade=crossfade)

        print("exporting bg")
        bg_track.export(f + ".wav")


def stitch():
    fg_track = AudioSegment.empty()
    bg_track = AudioSegment.empty()

    sil = AudioSegment.silent(duration=5000)
    padding = 1000
    intro_sound = AudioSegment.from_mp3("bell.mp3")

    bgs = glob("bg_audio/*.mp3")
    bg_sound = AudioSegment.from_mp3(random.choice(bgs))

    announcements = sorted(glob("recordings/*.effect.flac"))

    fg_track += sil

    for a in announcements:
        print("reading", a)
        part = (
            intro_sound.append(AudioSegment.from_file(a, format="flac"), crossfade=200)
            + sil
        )
        fg_track += part

        # fg_track += intro_sound
        # a = AudioSegment.from_file(a, format="flac")
        # # fg_track += a
        # fg_track = fg_track.append(a, crossfade=200)
        # fg_track += sil

    bg_dur = len(fg_track) + padding * 2

    print("making bg track")
    while len(bg_track) < bg_dur:
        crossfade = 5000

        if len(bg_track) == 0:
            crossfade = 0

        bg_track = bg_track.append(bg_sound, crossfade=crossfade)

    bg_track = bg_track[0:bg_dur]
    # bg_track = bg_track - 25

    print("overlaying tracks")
    final_track = bg_track.overlay(fg_track)  # , gain_during_overlay=-120)

    final_track = final_track.fade_in(1000).fade_out(1000)

    print("saving track")
    final_track.export("docs/radio.mp3", format="mp3")


def create_recordings(items):
    for country, text in items:

        print(country, text)
        safe_name = re.sub("[^aA-zZ]", "", country)

        outname = "recordings/{}.wav".format(safe_name)

        text = "Attention all passengers traveling to {}.\n{}".format(country, text)

        try:
            synthesize_ms(text, outname)

        except Exception as e:
            print(e)
            continue

        time.sleep(3)


def main():

    # add_effects()
    # generate_bgs()
    # stich2()
    # stitch()
    #
    # return False

    # items = get_data()
    # create_recordings(items)
    # add_effects()
    stitch2()


if __name__ == "__main__":
    main()
