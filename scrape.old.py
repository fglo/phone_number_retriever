import re
from sys import argv
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers.phonenumberutil import number_type, PhoneNumberType
import validators
from fake_useragent import UserAgent
from urllib3.util import Retry
from urllib.parse import urlparse

ua = UserAgent()

retry_strategy = Retry(
    total=5,
    status_forcelist=[408, 429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=1,
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

headers = {
    'User-Agent': str(ua.chrome)
}

pages_to_check = ['kontakt', 'skontaktujsieznami',
                  'skontaktujsie', 'contact', 'contactus', 'firma', 'company']

links_to_visit: list = []
visited_urls: list = []
last_visited_link: int = -1


def get_url_from_args():
    if len(argv) < 2:
        raise Exception('You need to pass an URL to the program.')
    if not validators.url(argv[1]):
        raise Exception('You need to pass a correct URL to the program.')
    return argv.pop(1)


def get_base_domain(url):
    hostname = urlparse(url).hostname
    return '' if hostname is None else hostname.split('.')[-2]


def get_base_url(url):
    parsed = urlparse(url)
    base_url = f'{parsed.scheme}://{parsed.hostname}'
    return base_url


def url_is_valid(url, base_domain):
    is_valid = url and url != '' and 'javascript:void(0)' not in url and get_base_domain(
        url) == base_domain
    return is_valid


def build_url(base_url, url):
    if not url:
        return None

    url = url.strip()
    if validators.url(url):
        return url
    if url[0] == '/':
        return f'{base_url}/{url[1:]}'
    return None


def get_links_from_page(html_doc, url):
    base_url = get_base_url(url)
    base_domain = get_base_domain(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    links = []
    for link in soup.findAll('a'):
        link_text = link.text.replace('\n', ' ').strip()
        link_url = build_url(base_url, link.get('href'))
        if url_is_valid(link_url, base_domain):
            links.append({'text': link_text, 'url': link_url.strip()})
    return links


def find_phone_numbers(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    scripts = ' '.join([script.text for script in soup.findAll('script')])
    text = soup.text + ' ' + scripts
    numbers_enumerator = phonenumbers.PhoneNumberMatcher(text, None)
    numbers = []
    for number in numbers_enumerator:
        escaped_number = number.raw_string.replace('+', '\+').replace('(', '\(').replace(
            ')', '\)').replace('[', '\[').replace('[', '\[').replace(' ', '\s?')
        headers = re.findall(rf'.*\s*:?\s*{escaped_number}', text)
        phoneNumber = phonenumbers.parse(number.raw_string)
        type = number_type(phoneNumber)
        type_str = PhoneNumberType.to_string(type)
        for header in headers:
            header = re.sub(rf'({escaped_number})|([\t\n])', '', header)
            numbers.append({'number': number.raw_string,
                           'header': header, 'type': type, 'type_str': type_str})
        if len(headers) == 0:
            numbers.append({'number': number.raw_string,
                           'header': '', 'type': type, 'type_str': type_str})
    return numbers


def normalize_page_name(name):
    return name.lower().replace(' ', '')


def link_comparer(e):
    return pages_to_check.index(normalize_page_name(e['text']))


def check_phone_number_header(header: str):
    header = header.lower().replace(' ', '')
    return 'biuro' in header or \
        'office' in header or \
        'büro' in header or \
        'recepcja' in header or \
        'reception' in header or \
        'frontdesk' in header or \
        'empfang' in header or \
        'rezeption' in header


def get_main_phone_number(phonenumbers):
    return next((phonenumber for phonenumber in phonenumbers if check_phone_number_header(phonenumber['header'])),
                next((phonenumber for phonenumber in phonenumbers if phonenumber['type'] == PhoneNumberType.FIXED_LINE),
                     phonenumbers[0]))


def get_page(url):
    global visited_urls
    visited_urls.append(url)
    html_doc = http.get(url, headers=headers, verify=True,
                        allow_redirects=True).text
    return html_doc


def filter_links(links):
    links = [link for link in links if normalize_page_name(
        link['text']) in pages_to_check and link['url'] not in visited_urls]
    return links


def find_links_to_visit(html_doc, url):
    global links_to_visit
    links = filter_links(get_links_from_page(html_doc, url))
    links.sort(key=link_comparer)
    links_to_visit.extend(links)


def get_urls_to_visit():
    global links_to_visit
    global last_visited_link
    while last_visited_link < len(links_to_visit) - 1:
        last_visited_link += 1
        yield links_to_visit[last_visited_link]['url']


def retrieve_phone_number():
    for url in get_urls_to_visit():
        html_doc = get_page(url)
        phonenumbers = find_phone_numbers(html_doc)
        if len(phonenumbers) > 0:
            return get_main_phone_number(phonenumbers)
        find_links_to_visit(html_doc, url)
    return None


def init():
    global links_to_visit
    global visited_urls
    global last_visited_link
    links_to_visit = []
    visited_urls = []
    last_visited_link = -1


def run():
    init()
    url = get_url_from_args()
    links_to_visit.append({'text': 'Main', 'url': url})
    phonenumber = retrieve_phone_number()
    print(None if phonenumber is None else phonenumber['number'])


if __name__ == '__main__':
    while len(argv) >= 2:
        run()
