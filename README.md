No Fly Zone
===========

This program creates a long (1h30 ish) audio WAV file from COVID-19 related
AIATA press releases, read by a text-to-speech program.

Running this program
--------------------

This program depends on a few audio processing tools, and will require you to
possess credentials for the google text-to-speech API.

### Tools

The following should install dependencies system-wide on an Ubuntu system:

```
sudo apt update && sudo apt install ffmpeg sox
```

### Python environment

Before running the program, you will need to create a virtualenv and install the
required python dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requireements.txt
```

### Actually running

Running the program can be easily done by calling the top-level `run.sh` script.

The script will take care of activating your virtualenv should that not already
be done.


Text-to-speech
--------------

By default, Google's text-to-speech API is used, but code exists to leverage
Microsoft's equivalent API instead.

Have a look in `generate.py` if that is of interest to you.
