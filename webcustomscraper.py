import json
from datetime import datetime
from pprint import pprint

import html2text
import requests as requests
from bs4 import BeautifulSoup


# customtemplate - name as your context needs it
def fill_and_get_customtemplate_from(url, date_acessed, title: str, body_text: str, links) -> dict:
    # NOTE: validation should have happened way before so here should not take place any
    return {
        "url": url,
        "date_acessed": date_acessed,
        "content": body_text,
        "title": title,
        "links": links,
    }


def scrape_webresponse(input_url: str) -> requests.Response:
    # TODO: still validations

    result = requests.get(input_url)
    result.raise_for_status()
    return result


def scraped_webcontent_to_json(parsed_webcontent: BeautifulSoup, ignore_links=True, bypass_tables=False) -> dict:
    # TODO: still validations

    # setup html2text
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = ignore_links
    text_maker.bypass_tables = bypass_tables

    # let's shape our data
    webcontent_urls = [x.get('href') for x in parsed_webcontent.findAll(
        'a')]  # TODO: As you can see there are lots of seemingly non-openable urls, that needs a prefilter...
    
    result = fill_and_get_customtemplate_from(None,
                                              datetime.now().isoformat(),
                                              text_maker.handle(str(parsed_webcontent.title).strip()),
                                              text_maker.handle(str(parsed_webcontent.body).strip()),
                                              # TODO: Content here needs to be splitted if necessary
                                              webcontent_urls)
    return result


def add_meta_to(scraped_webresponse: requests.Response, converted_webcontent: dict):
    converted_webcontent["url"] = scraped_webresponse.url


def scrape_html_to_customtemplate(input_url: str) -> json:
    # TODO: inputcheck goes here for - empty; valid; etc.

    # simply download the INTERNET
    scraped_webresponse = scrape_webresponse(input_url)
    parsed_webcontent = BeautifulSoup(scraped_webresponse.content, "html.parser")

    # NOTE: for one edge-cases, you have the power to simply call `scraped_webcontent.json()` which returns you -
    #  u guessed, an actual json, tho it's only possible when the data IS COMING already as a json.
    #  Take this as an eg.: requests.get('https://api.github.com/events').json()
    converted_webcontent = scraped_webcontent_to_json(parsed_webcontent)
    add_meta_to(scraped_webresponse, converted_webcontent)

    return converted_webcontent


if __name__ == "__main__":
    simple_url = "https://stackoverflow.com/questions/3075550/how-can-i-get-href-links-from-html-using-python"
    pprint("Scraped content looks like: {}".format(scrape_html_to_customtemplate(simple_url)))

"""example
    <!DOCTYPE html>
<html>
<head>
<meta dabhdjahjdnalk/>
</head>
<body>

<h2>The href Attribute</h2>

<p>HTML links are defined with the a tag. The link address is specified in the href attribute:</p>

<a href="https://www.w3schools.com">Visit <em>W3Schools</em> <b> sakjdhasjk</b></a>

</body>
</html>

{
	"url": "http://www.example.com",
	"date_acessed": "2022-05-01T00:00:00:0000Z",
	"content": [
		"The href Attribute",
		"HTML links are defined with the a tag. The link address is specified in the href attribute:",
		"Visit W3Schools"
	],
	"links": [
		"https://www.w3schools.com"
	],
	"meta": [
		{key: "something", "value": "something else"},

	]
}
    """
