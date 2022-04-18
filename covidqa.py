import sys
from termcolor import colored
from webquery import bing
from bertqa import qaapi


def covid_qa_system(question: str, query: str = '') -> list:
    """Works by doing question analysis, search with Bing for most relevant documents
    and uses a fine-tuned BERT model to highlight the answer in the returned snippets.
    In testing mode, if `query` is specified, use it instead of the automatically
    generated one."""
    processed_question = bing.bing_search_v7(question, query)
    results = []

    for hit in processed_question:
        answer, confid, new_snippet = qaapi.bert_response_highlight(
            question, context=hit['snippet'])
        r = hit['rank']
        hit['snippet'] = new_snippet
        hit['answer'] = answer
        hit['confidence'] = confid * ((10. - r) / 10.)
        hit['start_offset'] = new_snippet.index(answer)
        hit['end_offset'] = hit['start_offset'] + len(answer)

        if hit['confidence'] < 0.3 and len(results) > 3:
            # Cut off uninteresting results.
            break
        # end if

        results.append(hit)
    # end for

    # Sort answers by relevance
    return sorted(results, key=lambda x: x['confidence'], reverse=True)


def print_answers(answers: list):
    for hit in answers:
        title_colored = colored(
            hit['name'], color='yellow', attrs=['bold'])
        print(title_colored)
        url_colored = colored(hit['url'], color='blue')
        print(url_colored)
        snippet = hit['snippet']
        answer = hit['answer']
        aidx = snippet.index(answer)
        left_text = snippet[:aidx]
        right_text = snippet[aidx + len(answer):]
        answer_colored = colored(answer, color='red')
        cfd = hit['confidence']
        confid_colored = colored(f'{cfd:.5f}', on_color='on_cyan', attrs=['bold'])
        print(left_text, end='')
        print(answer_colored, end='')
        print(right_text)
        print('Confidence: ', end='')
        print(confid_colored)
        print(flush=True)
    # end for



if __name__ == '__main__':
    bing._debug = False
    qaapi._debug = False

    print(f'> ', flush=True, end='')
    line = sys.stdin.readline().strip()

    while line.lower() != 'exit' and line.lower() != 'quit':
        if line:
            qa_results = covid_qa_system(line)
            print_answers(qa_results)
            print(flush=True)
        # end if
       
        print(f'> ', flush=True, end='')
        line = sys.stdin.readline().strip()
    # end while
