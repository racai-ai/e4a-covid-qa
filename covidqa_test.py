import os
import sys
from glob import glob
from time import sleep
from Levenshtein import seqratio
from regex import F
from covidqa import covid_qa_system
from webquery import normalize_words


def read_test_file(test_file: str) -> list[dict]:
    """Reads a test file, with the format of question/snippet/answer(s)."""

    examples = []

    with open(test_file, mode='r', encoding='utf-8') as f:
        while True:
            question = f.readline().strip()

            if not question:
                break
            # end if

            url_answers = []
            url = f.readline().strip()

            while url.startswith('http'):
                snippet = f.readline().strip()
                answers = []
                prev_sqb2 = -1

                try:
                    while True:
                        if prev_sqb2 >= 0:
                            sqb1 = snippet.index('[', prev_sqb2 + 1)
                        else:
                            sqb1 = snippet.index('[')
                        # end if

                        sqb2 = snippet.index(']', sqb1 + 1)
                        answer = snippet[sqb1 + 1:sqb2]
                        answers.append(answer)
                        prev_sqb2 = sqb2
                    # end while
                except ValueError:
                    pass
                # end try

                snippet = snippet.replace('[', '')
                snippet = snippet.replace(']', '')

                url_answers.append({
                    'url': url,
                    'snippet': snippet,
                    'answers': answers
                })
                url = f.readline().strip()
            # end while

            if url == 'N/A':
                examples.append({
                    'question': question,
                    'qasys': 'N/A'
                })
                f.readline()
            else:
                examples.append({
                    'question': question,
                    'qasys': url_answers
                })
            # end if
        # end while
    # end with

    return examples


def read_test_folder(test_folder: str) -> list:
    """Reads the test files that were created by humans.
    Each file has one question/the human query/the snippet with the correct
    answer highlighted with [...]."""

    test_examples = []

    for f in glob(os.path.join(test_folder, '*.txt')):
        test_examples.extend(read_test_file(f))
    # end for

    return test_examples


def _seq_lcs(aseq: list, bseq: list) -> list:
    longest_sequence = []
    lsq_max = 0

    for i in range(len(aseq)):
        for j in range(len(bseq)):
            x = i
            y = j
            lseq = []

            while aseq[x] == bseq[y]:
                lseq.append(aseq[x])
                x += 1
                y += 1

                if x == len(aseq) or y == len(bseq):
                    break
                # end if
            # end while

            lsq_len = sum([len(x) for x in lseq])

            if lsq_len > lsq_max:
                longest_sequence = lseq
                lsq_max = lsq_len
            # end if
        # end for
    # end for

    return longest_sequence


def evaluate_example(example: dict, responses: list) -> tuple:
    """Takes an ground truth example and a list of responses and
    returns an evaluation dict."""

    found_doc_rank = -1
    overlap_span = ''

    if example['qasys'] == 'N/A':
        return found_doc_rank, '', '', ''
    # end if

    for r, hit in enumerate(responses):
        for qas in example['qasys']:
            if hit['url'] == qas['url']:
                found_doc_rank = r
                break
            # end if
        # end for

        if found_doc_rank >= 0:
            break
        # end if
    # end for

    best_human_answer = ''
    best_bert_answer = ''

    if found_doc_rank >= 0:
        for hit in responses:
            qa_answer = normalize_words(hit['answer'].split())

            for qas in example['qasys']:
                if hit['url'] == qas['url']:
                    for answer in qas['answers']:
                        ex_answer = normalize_words(answer.split())
                        # Compute answer overlap
                        lcs = _seq_lcs(qa_answer, ex_answer)
                        overlap_lcs = ' '.join(lcs)

                        if len(overlap_lcs) > len(overlap_span):
                            overlap_span = overlap_lcs
                            best_human_answer = ' '.join(ex_answer)
                            best_bert_answer = ' '.join(qa_answer)
                        # end if
                    # end for
                # end if
            # end for
        # end for
    # end if

    return found_doc_rank, overlap_span, best_human_answer, best_bert_answer


if __name__ == '__main__':
    input_folder = os.path.join('data', 'test_v7')
    test_set = read_test_folder(input_folder)
    mrr = 0
    exact = 0
    correct_chars = 0
    predicted_chars = 0
    annotated_chars = 0
    
    for ex in test_set:
        sleep(3)
        q = ex['question']
        print(f'Running question [{q}]', file=sys.stderr, flush=True)
        qa_results = covid_qa_system(q)
        drnk, ospn, hans, bans = evaluate_example(example=ex, responses=qa_results)

        if drnk >= 0:
            mrr += 1 / (drnk + 1)

            if hans == bans:
                exact += 1
            # end if

            correct_chars += len(ospn)
            predicted_chars += len(bans)
            annotated_chars += len(hans)
        # end if
    # end for

    mrr /= len(test_set)
    exact /= len(test_set)
    prec = correct_chars / predicted_chars
    rec = correct_chars / annotated_chars
    f1 = 2 * prec * rec / (prec + rec)

    print(f'MRR = {mrr:.5f}')
    print(f'Exact = {exact:.5f}')
    print(f'P(overlap) = {prec:.5f}')
    print(f'R(overlap) = {rec:.5f}')
    print(f'F1(overlap) = {f1:.5f}')
