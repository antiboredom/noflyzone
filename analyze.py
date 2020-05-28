from glob import glob
import json
from pprint import pprint
import re
import spacy
import csv
from generate import get_data

nlp = spacy.load("en_core_web_sm")

with open("country-names.txt", "r") as infile:
    countries = infile.readlines()
    countries = [c.strip() for c in countries]

country_pat = "|".join(countries)

filename = sorted(glob("data/*.txt"))[-1]
items = get_data(filename)

results = {}

for country, data in items:
    country = country.upper()
    print(country)

    doc = nlp(data)
    results[country] = {"bad": [], "good": [], "transit": [], "quarantine": []}
    for sent in doc.sents:
        # print(sent.string)
        names = re.findall(country_pat, sent.string, flags=re.IGNORECASE)
        names = [n.upper() for n in names]
        names = [n for n in names if n != country]
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


print(results)
print('----')

with open("countries.csv", "r") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        name = row["name"].upper()
        print(name)
        if name in results:
            results[name]["lat"] = float(row["lat"])
            results[name]["lon"] = float(row["lon"])
        else:
            results[name] = {"bad": [], "good": [], "transit": [], "quarantine": []}
            try:
                results[name]["lat"] = float(row["lat"])
                results[name]["lon"] = float(row["lon"])
            except Exception as e:
                print(e)
                continue


with open("docs/parsed_results.json", "w") as outfile:
    json.dump(results, outfile)
