import sys
import requests
import json

teprolin_url = 'http://relate.racai.ro:5000/process'

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
            result.append((tk['_id'], tk['_wordform'], tk['_ctg'], tk['_head'], tk['_deprel']))
        # end for

        return result
    else:
        print(
            f'Error processing question [{question} with TEPROLIN; error code {response.status_code}]',
            file=sys.stderr, flush=True)
        return []
