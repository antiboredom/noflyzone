import re
import time
import json

from subprocess import call
from requests_html import HTMLSession

import requests

# Uncomment the following line if you would rather use MSFT's library for
# text-to-speech.
# import mstextexample

from google.cloud import texttospeech
client = texttospeech.TextToSpeechClient()


HIDE_DATE = True

with open("text-to-speech-key.json", "r") as infile:
    KEYS = json.load(infile)


def get_data():
    """Grab and parse the data from the desired page on the IATA website."""
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
    """Call Google's API for text-to-speech.

    This calls google cloud's API to perform text-to-speech and dump
    the created .wav file into the desired outname."""
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    voice = texttospeech.types.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C",
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
        speaking_rate=1.0,
        pitch=1.0,
    )

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    with open(outname, "wb") as out:
        out.write(response.audio_content)


def synthesize_local(text, outname):
    """This is unused."""
    call(["say", "-o", outname, text])
    return outname

def synthesize_ms(text, outname):
    """Calls Microsoft's API for text-to-speech.

    This is currently unused."""
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


def main():

    items = get_data()

    for country, text in items:

        # print(country, text)
        safe_name = re.sub("[^aA-zZ]", "", country)

        outname = f"recordings/{safe_name}.wav"

        text = country + "... \n" + text

        try:
            # Uncomment the following line to use the microsoft API
            # synthesize_ms(text, outname)

            # Comment the following line if you do not want to use Google's API.
            synthesize_google(text, outname)

            print(f"Wrote out {outname}")
        except Exception as e:
            print(e)

        # UNcomment the following should you wish to use the microsoft API.
        # time.sleep(3)


if __name__ == "__main__":
    main()
