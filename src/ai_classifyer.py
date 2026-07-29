from collections import Counter

TOPIC_KEYWORDS = {
    "Marriage": [
        "marriage","wife","husband","divorce","relationship","love","counseling",
        "therapy","married","reconcile","separation","basement"
    ],
    "Children": [
        "colin","latham","school","rowing","homework","practice","cba"
    ],
    "Financial": [
        "money","bank","fidelity","rockefeller","tax","income","pay","wire",
        "mortgage","credit","cash","budget","expense"
    ],
    "House": [
        "house","home","garage","barn","basement","kitchen","driveway",
        "construction","contractor"
    ],
    "Farm": [
        "horse","goat","arena","pasture","tractor","kubota","hay","fence",
        "stall","farm"
    ],
    "Travel": [
        "hotel","flight","airport","vacation","trip","drive","boat"
    ],
    "Medical": [
        "doctor","hospital","medicine","health","covid","surgery"
    ],
    "Legal": [
        "lawyer","attorney","court","legal","agreement","custody","mediation"
    ]
}


def classify_messages(messages):
    text = " ".join(m.text.lower() for m in messages if m.text)

    found = []

    for topic, words in TOPIC_KEYWORDS.items():
        for word in words:
            if word in text:
                found.append(topic)
                break

    return " | ".join(sorted(found)) if found else "General"