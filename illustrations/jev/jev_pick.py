"""
jev_pick.py — ask Jev (TypeSafe) which illustration a piece of copy should carry.

Jev is text-only: it judges the DESCRIPTIONS in catalogue.json, not the
pictures. So the catalogue is the real design decision; Jev applies it
consistently.

Setup (on your own machine — never paste the key into a chat or a file):
    pip install requests
    Windows PowerShell:  $env:TYPESAFE_API_KEY = "…"
    then:                python jev_pick.py sections.json

sections.json:
    {"hero": "You built your business on instinct. Grow it on evidence. …",
     "service-03": "Testing whether it's real. Finding out whether a pattern …"}

For each section it prints Jev's pick, its probability, and whether any image
fits at all. A pick under 0.6 is a question for a person, not an answer.
"""

import json
import os
import sys

import requests

API = "https://api.typesafe.ai/v1/systemone"
HERE = os.path.dirname(os.path.abspath(__file__))


def ask(state, catalogue):
    body = {
        "model": "jev-latest",
        "state": state,
        "questions": {
            "illustration": {
                "type": "choice",
                "instructions": ("Which illustration's MEANING best reinforces the message of this "
                                 "website section. Judge the meaning, not the look. Choose 'none' "
                                 "when the section is operational or no meaning fits."),
                "criteria": catalogue,
            },
            "reinforces": {
                "type": "noul",
                "instructions": ("An illustration with a specific meaning would strengthen this "
                                 "section's argument, rather than decorate it"),
            },
        },
    }
    r = requests.post(API, json=body, timeout=30,
                      headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"})
    r.raise_for_status()
    return r.json()


def main():
    if "TYPESAFE_API_KEY" not in os.environ:
        sys.exit("Set TYPESAFE_API_KEY in your environment first (see the top of this file).")
    catalogue = {k: v for k, v in json.load(open(os.path.join(HERE, "catalogue.json"), encoding="utf-8")).items()
                 if not k.startswith("_")}
    sections = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "sections.json"),
                              encoding="utf-8"))
    results = {}
    for name, text in sections.items():
        res = ask(text, catalogue)
        results[name] = res
        # The response shape is printed raw once so we can map it exactly; see README.
        print(f"\n== {name}\n{json.dumps(res, indent=2, ensure_ascii=False)[:1500]}")
    json.dump(results, open(os.path.join(HERE, "jev_results.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print("\nSaved jev_results.json — send it back and I'll wire the picks into the site.")


if __name__ == "__main__":
    main()
