import re
import time
from subprocess import call
from requests_html import HTMLSession

HIDE_DATE = True


def get_data():
    session = HTMLSession()
    r = session.get(
        "https://www.iatatravelcentre.com/international-travel-document-news/1580226297.htm"
    )

    content = r.html.find(".middle", first=True).text


    content = re.sub("\n{2,}", "\n\n", content)

    items = re.split("\n\n", content)

    items = [i for i in items if re.search("[A-Z]+ - published", i)]

    content = content.replace(" (COVID-19)", "")

    content = content.replace(" COVID-19", "covid nineteen")

    if HIDE_DATE:
        items = [re.sub(" - published .*", "", i) for i in items]

    items = [i.split("\n") for i in items]

    items = [(i[0], "\n".join(i[1:])) for i in items]

    return items


def main():

    items = get_data()
    for country, text in items:
        print(country, text)
        outname = country + ".aiff"
        call(["say", "-o", outname, country + ".  \n" + text])


if __name__ == "__main__":
    main()
