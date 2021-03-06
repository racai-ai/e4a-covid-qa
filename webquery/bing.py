import os
import sys
import requests
import random
import string
from glob import glob
from time import perf_counter
from . import process_question_with_teprolin, \
    remove_diacritics, frequent_verbs


_bing_search_url = 'https://api.bing.microsoft.com/v7.0/search?q=#QUERY#&cc=RO'
_bing_api_key = os.getenv('BING_SEARCH_V7_KEY')
_debug = True

# 1. Check for valid Bing API key
if not _bing_api_key:
    raise RuntimeError(
        "No Bing API key was found in environment variable BING_SEARCH_V7_KEY!")
# end if

# 2. Create multiprocess Bing query caches
_cache_unique_key = ''

while len(_cache_unique_key) < 8:
    _cache_unique_key += random.choice(string.ascii_lowercase + string.digits)
# end while

_bing_cache_file = os.path.join('cache', f'bing-{_cache_unique_key}.txt')
_bing_master_cache_file = os.path.join('cache', f'bing-master.txt')
_bing_cache = {}
_cache_additions = 0

def _add_cache_file(cache_file: str):
    """Adds a Bing cache file to the current cache."""

    with open(cache_file, mode='r', encoding='utf-8') as f:
        line = f.readline().strip()

        while True:
            query = line
            query_hits = []
            line = f.readline().strip()

            while line and line != '#EOR#':
                hit_dict = {}
                hit_dict['name'] = line
                hit_dict['url'] = f.readline().strip()
                hit_dict['snippet'] = f.readline().strip()
                hit_dict['date'] = f.readline().strip()
                hit_dict['rank'] = len(query_hits)
                query_hits.append(hit_dict)
                line = f.readline().strip()
            # end while

            if not line:
                break
            # end if
            
            _bing_cache[query] = query_hits
            line = f.readline().strip()
        # end for
    # end with
# end def

# 2.1 Load the cache for Bing queries
for f in glob(os.path.join('cache', 'bing-*.txt')):
    _add_cache_file(f)

    if not f.endswith(_bing_master_cache_file):
        print(f'Deleting previous cache file [{f}]', file=sys.stderr, flush=True)
        os.remove(f)
    # end if
# end for

def _save_cache_file(cache_file: str):
    """Saves the `_bing_cache` dict to the `cache_file` file."""

    with open(cache_file, mode='w', encoding='utf-8') as f:
        for query in sorted(list(_bing_cache.keys())):
            print(query, file=f)

            for hit_dict in _bing_cache[query]:
                print(hit_dict['name'], file=f)
                print(hit_dict['url'], file=f)
                print(hit_dict['snippet'], file=f)
                print(hit_dict['date'], file=f)
            # end for

            print('#EOR#', file=f, flush=True)
        # end for
    # end with
# end def


# 2.2 Write master file back
_save_cache_file(_bing_master_cache_file)


def _generate_query_1(tokens: list) -> str:
    """Takes a processed question and generates a web search query from it.
    For now, just choose the nouns in the question."""

    query = []

    for tid, wf, lem, ctag, head, deprel in tokens:
        if ctag == 'NOUN' or ctag == 'PROPN' or ctag == 'ADJ' or \
                ctag == 'NUM' or ctag == 'ADV' or \
                (ctag == 'VERB' and lem not in frequent_verbs):
            query.append(wf)
        # end if
    # end for

    return ' '.join(query)


def bing_search_v7(question: str, given_query: str) -> list:
    """Performs a Bing V7 search for the given question.
    If question is in cache, no search request is sent.
    If `given_query` is not empty, use it instead of generating the query.
    This is useful when testing the QA system with human generated queries."""

    if given_query:
        return _do_the_web_search(given_query)
    # end if

    # 1. Process question
    q_tokens = process_question_with_teprolin(question)

    # 2. Generate query
    q_query = _generate_query_1(q_tokens)
    ndq_query = remove_diacritics(q_query)
    
    if q_query == ndq_query:
        if q_query in _bing_cache:
            # Spare Bing API querying...
            return _bing_cache[q_query]
        else:
            return _do_the_web_search(q_query)
        # end if
    else:
        results = []

        if q_query in _bing_cache:
            # Spare Bing API querying...
            results.extend(_bing_cache[q_query])
        else:
            results.extend(_do_the_web_search(q_query))
        # end if

        if ndq_query in _bing_cache:
            # Spare Bing API querying...
            results.extend(_bing_cache[ndq_query])
        else:
            results.extend(_do_the_web_search(ndq_query))
        # end if

        return _remove_duplicate_hits(results)
    # end if


def _do_the_web_search(query: str) -> list:
    """Does the Bing search and returns the list of results."""
    global _cache_additions

    # 1. Populate query link
    bing_query_url = _bing_search_url.replace('#QUERY#', query)

    if _debug:
        # 2. Do the query
        print(f'Querying Bing with query [{query}]', file=sys.stderr, flush=True)
        start = perf_counter()
    # end if
    response = requests.get(bing_query_url, headers={
                            "Ocp-Apim-Subscription-Key": _bing_api_key})

    if _debug:
        elapsed = 1000 * (perf_counter() - start)
        print(f' -> took {elapsed:.3f}ms', file=sys.stderr, flush=True)
    # end if

    if response.status_code == 200:
        bing_json = response.json()

        if 'webPages' in bing_json and \
                'value' in bing_json['webPages']:
            results = []
            rank = 0

            for hit in bing_json['webPages']['value']:
                hit_dict = {'rank': rank}
                hit_dict['name'] = hit['name']
                hit_dict['url'] = hit['url']
                hit_dict['snippet'] = hit['snippet']
                hit_dict['date'] = hit['dateLastCrawled']
                results.append(hit_dict)
                rank += 1
            # end for

            _bing_cache[query] = results
            _cache_additions += 1

            if _cache_additions % 10 == 0:
                _save_cache_file(_bing_cache_file)
            # end if

            return results
    else:
        print(
            f'Error querying Bing with [{query}; error code {response.status_code}]',
            file=sys.stderr, flush=True)
        return []


def _remove_duplicate_hits(search_results: list) -> list:
    results = []
    url_set = set()

    for hit in search_results:
        if hit['url'] not in url_set:
            results.append(hit)
            url_set.add(hit['url'])
        # end if
    # end for

    return results
