from webquery.bing import bing_search_v7
from bertqa.qaapi import bert_response_highlight


def covid_qa_system(question: str) -> list:
    """Works by doing question analysis, search with Bing for most relevant documents
    and uses a fine-tuned BERT model to highlight the answer in the returned snippets."""
    processed_question = bing_search_v7(question)
    results = []

    for r, hit in enumerate(processed_question):
        answer, confid, new_snippet = bert_response_highlight(
            question, context=hit['snippet'])
        hit['snippet'] = new_snippet
        hit['answer'] = answer
        hit['confidence'] = confid * ((10. - r) / 10.)
        hit['start_offset'] = new_snippet.index(answer)
        hit['end_offset'] = hit['start_offset'] + len(answer)
        results.append(hit)
    # end for

    # Sort answers by relevance
    return sorted(results, key=lambda x: x['confidence'], reverse=True)


if __name__ == '__main__':
    question = 'Cum pot face Covid?'
    qa_results = covid_qa_system(question)
