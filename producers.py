import pickle


PRODUCER_STATS = {
    "bank": {
        "delay": 5,
        "value": 10,
        "cost": 100
    },
    "hotel": {
        "delay": 10,
        "value": 40,
        "cost": 200
    },
    "casino": {
        "delay": 20,
        "value": 160,
        "cost": 400
    }
}

DEFAULT_PRODUCERS = {
    "bank": 0,
    "hotel": 0,
    "casino": 0
}


def default_producers_to_text():
    return producers_to_text(DEFAULT_PRODUCERS)


def producers_to_text(producers):
    return pickle.dumps(producers)


def text_to_producers(text):
    producers = pickle.loads(text)

    for producer in DEFAULT_PRODUCERS:
        if producer not in producers:
            producers[producer] = DEFAULT_PRODUCERS[producer]

    return producers
