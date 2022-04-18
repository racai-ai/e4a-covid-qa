import sys
import requests
from time import perf_counter


_bert_qa_url = 'http://127.0.0.1:31415/predict'
_debug = True


def bert_response_highlight(question: str, context: str) -> tuple:
    if _debug:
        print(f'Querying BERT QA API with question [{question}]', file=sys.stderr, flush=True)
        start = perf_counter()
    # end if
    
    response = requests.post(_bert_qa_url, json={'document': context, 'question': question})
    
    if _debug:
        elapsed = 1000 * (perf_counter() - start)
        print(f' -> took {elapsed:.3f}ms', file=sys.stderr, flush=True)
    # end if

    if response.status_code == 200:
        bert_json = response.json()

        if 'result' in bert_json:
            sidx = bert_json['result']['start']
            eidx = bert_json['result']['end']
            tokenized_document = bert_json['result']['document']
            exact_answer = ' '.join(tokenized_document[sidx:eidx + 1])
            confidence = bert_json['result']['confidence']
            new_context = ' '.join(tokenized_document)

            return (exact_answer, confidence, new_context)
        else:
            print(f'No result from BERT QA API for question [{question}]', file=sys.stderr, flush=True)
        # end if
    else:
        print(f'Error from BERT QA API for question [{question}]', file=sys.stderr, flush=True)
    # end if

    return ('', 0.)
