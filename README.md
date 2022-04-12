## e4a-covid-qa
An open QA system, for Romanian, answering open-ended questions about COVID-19.
Works by interrogating Bing with a Romanian question to query algorithm, returning the top 10 text snippets.
Using a COVID-19 fine-tuned BERT model, the most probable answer(s) are sent back to the user.

## Usage
You need a Bing V7 search API key that is valid and that is stored in the environment variable `BING_SEARCH_V7_KEY`.

The main entrypoint in the Python 3 code is `covidqa.covid_qa_system()` method which takes a `str` question and returns a list of dictionaries, each with probable answer information. A dictionary from this list looks like this:

```json
{
    "name": "Infectarea cu COVID-19 în timpul sarcinii îți poate afecta ...",
    "url": "https://doc.ro/sanatate/infectarea-cu-covid-19-in-timpul-sarcinii-iti-poate-afecta-bebelusul",
    "snippet": "Tratamentul pentru COVID-19 este similar cu tratamentul altor boli respiratorii. Indiferent dacă ești însărcinată sau nu, medicii recomandă: acetaminofen (Paracetamol) pentru o febră de 38°C sau mai mare hidratare cu apă sau băuturi cu conținut scăzut de zahăr odihnă",
    "date": "2022-03-19T19:53:00.0000000Z",
    "answer": "Tratamentul pentru COVID-19 este similar cu tratamentul altor boli respiratorii.",
    "confidence": 0.9542,
    "start_offset": 0,
    "end_offset": 80
}
```

## Acknowledgements
Developed in the [Enrich4All project](https://www.enrich4all.eu/), for Romanian COVID-19 questions. To be extended to new languages and domains.
