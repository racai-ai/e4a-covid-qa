import re
import sys
import requests
import json

teprolin_url = 'http://relate.racai.ro:5000/process'
frequent_verbs = set([
    'fi', 'avea', 'putea'
])
_punct_left_rx = re.compile('^\\W+')
_punct_right_rx = re.compile('\\W+$')


def process_question_with_teprolin(question: str) -> list:
    """Takes an input questions and does POS tagging and dependency parsing
    with the TEPROLIN web service from http://relate.racai.ro:5000."""

    question = question.strip()
    response = requests.post(url=teprolin_url, data={
                               'text': question, 'exec': 'dependency-parsing'})
    
    if response.status_code == 200:
        json_response = json.loads(response.text)
        tokens = json_response['teprolin-result']['tokenized'][0]
        result = []

        for tk in tokens:
            result.append((tk['_id'], tk['_wordform'], tk['_lemma'], tk['_ctg'], tk['_head'], tk['_deprel']))
        # end for

        return result
    else:
        print(
            f'Error processing question [{question} with TEPROLIN; error code {response.status_code}]',
            file=sys.stderr, flush=True)
        return []


def remove_diacritics(query: str) -> str:
    query = query.replace('ă', 'a')
    query = query.replace('â', 'a')
    query = query.replace('Ă', 'A')
    query = query.replace('Â', 'A')
    query = query.replace('î', 'i')
    query = query.replace('Î', 'I')
    query = query.replace('ș', 's')
    query = query.replace('Ș', 'S')
    query = query.replace('ț', 't' )
    query = query.replace('Ț', 'T')
    
    return query


def normalize_words(word_sequence: list) -> list:
    """Takes a list of Romanian words and prepares them for word sequence overlap."""

    result = []

    for w in word_sequence:
        w = remove_diacritics(w)
        w = _punct_left_rx.sub('', w)
        w = _punct_right_rx.sub('', w)

        if len(w) > 3:
            result.append(w.lower())
        # end if
    # end for

    return result

