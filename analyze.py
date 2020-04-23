from glob import glob
import json
from pprint import pprint
import re
import spacy
import csv

nlp = spacy.load("en_core_web_sm")

with open("country-names.txt", "r") as infile:
    countries = infile.readlines()
    countries = [c.strip() for c in countries]

country_pat = "|".join(countries)

filename = sorted(glob("data/*.txt"))[-1]
with open(filename, "r") as infile:
    content = infile.read()

content = re.sub("\n{2,}", "\n\n", content)
content = re.sub("\(.*?\)", " ", content)
content = content.replace("–", "-")
items = re.split("\n\n", content)
items = [i for i in items if re.search("[A-Z]+ - published", i)]
content = content.replace(" (COVID-19)", "")
content = content.replace(" COVID-19", "covid nineteen")
items = [re.sub(" - published .*", "", i) for i in items]
items = [i.split("\n") for i in items]
items = [(i[0], "\n".join(i[1:])) for i in items]


results = {}

for country, data in items:
    print(country)

    doc = nlp(data)
    results[country] = {"bad": [], "good": [], "transit": [], "quarantine": []}
    for sent in doc.sents:
        # print(sent.string)
        names = re.findall(country_pat, sent.string, flags=re.IGNORECASE)
        names = [n for n in names if n.upper() != country.upper()]
        names = sorted(list(set(names)))

        if "quarantine" in sent.string:
            results[country]["quarantine"] += names
            continue

        if "not allowed" in sent.string:
            results[country]["bad"] += names
            continue

        if "not apply" in sent.string:
            # if "transit" in sent.string:
            #     results[country]["transit"] += names
            # else:
            #     results[country]["good"] += names
            results[country]["good"] += names


print('----')

with open("countries.csv", "r") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        name = row["name"].upper()
        if name in results:
            results[name]["lat"] = float(row["lat"])
            results[name]["lon"] = float(row["lon"])
        else:
            print(name)
            results[name] = {"bad": [], "good": [], "transit": [], "quarantine": []}
            try:
                results[name]["lat"] = float(row["lat"])
                results[name]["lon"] = float(row["lon"])
            except Exception as e:
                print(e)
                continue


with open("docs/parsed_results.json", "w") as outfile:
    json.dump(results, outfile)
