nlp = spacy.load("en_core_web_sm")

def named_entity_recognition(text, label):
    document = nlp(text)
    return [entities.text for entities in document.ents if entities.label_ == label]

def top_entities(text, label, top = 10):
    ents = text.apply(lambda x: named_entity_recognition(x, label))
    ents = [i for x in ents for i in x]
    counter = Counter(ents)
    return counter.most_common(top)



    # under song statistics:
        # Named Entity Recognition
    top_people = top_entities(lyrics, "PEOPLE", 5)