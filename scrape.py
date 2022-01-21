from sys import argv
from typing import Optional
import re
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers.phonenumberutil import number_type, PhoneNumberType
import validators
from fake_useragent import UserAgent
from urllib3.util import Retry
from urllib.parse import urlparse

UA = UserAgent()

RETRY_STRATEGY = Retry(
    total=5,
    status_forcelist=[408, 429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=1,
)
HTTP_ADAPTER = HTTPAdapter(max_retries=RETRY_STRATEGY)
HTTP = requests.Session()
HTTP.mount("https://", HTTP_ADAPTER)
HTTP.mount("http://", HTTP_ADAPTER)

HEADERS = {'User-Agent': str(UA.chrome)}

PAGES_TO_CHECK = ['kontakt', 'skontaktujsieznami', 'skontaktujsie',
                  'contact', 'contactus', 'firma', 'company', 'onas', 'aboutus']
OFFICE_HEADER_FRAGMENTS = ['biuro', 'office', 'büro',
                           'recepcja', 'reception', 'frontdesk', 'empfang', 'rezeption']


class PhoneNumber:
    def __init__(self, number, header=''):
        parsed_number = phonenumbers.parse(number)
        self.number = number
        self.header = header
        self.type = number_type(parsed_number)
        self.type_str = PhoneNumberType.to_string(self.type)

    def is_office_number(self) -> bool:
        header = self.header.lower().replace(' ', '')
        return any(fragment in header for fragment in OFFICE_HEADER_FRAGMENTS)

    def is_fixed_line(self) -> bool:
        return self.type == PhoneNumberType.FIXED_LINE

    @staticmethod
    def get_main_phone_number(phone_number_list):
        office_number_generator = (phone_number for phone_number in phone_number_list if phone_number.is_office_number())
        fixed_line_number_generator = (phone_number for phone_number in phone_number_list if phone_number.is_fixed_line())
        return next(office_number_generator, next(fixed_line_number_generator, phone_number_list[0]))

    @staticmethod
    def escape_number(number: str) -> str:
        return number.replace('+', '\+') \
            .replace('(', '\(') \
            .replace(')', '\)') \
            .replace('[', '\[') \
            .replace('[', '\[') \
            .replace(' ', '\s?')


class Link:
    def __init__(self, text, url):
        self.text = text
        self.normalized_text = text.lower().replace(' ', '')
        self.url = url

    @staticmethod
    def comparer(link) -> int:
        return PAGES_TO_CHECK.index(link.normalized_text)


class WebPage:
    def __init__(self, start_url):
        if not validators.url(start_url):
            raise Exception('You need to pass a correct URL.')

        self.links_to_visit: list[Link] = [Link('MAIN', start_url)]
        self.visited_urls: list[str] = []
        self.last_visited_link = -1

        parsed = urlparse(start_url)
        self.base_domain = '' if not parsed.hostname else parsed.hostname.split('.')[-2]
        self.base_url = f'{parsed.scheme}://{parsed.hostname}'

    def get_base_domain(self, url: str):
        hostname = urlparse(url).hostname
        return '' if not hostname else hostname.split('.')[-2]

    def get_base_url(self, url: str):
        parsed = urlparse(url)
        base_url = f'{parsed.scheme}://{parsed.hostname}'
        return base_url

    def is_url_valid(self, url: str):
        is_valid = url and 'javascript:void(0)' not in url and self.get_base_domain(
            url) == self.base_domain
        return is_valid

    def format_url(self, url: str, parent_url: str) -> str:
        if not url:
            return url

        url = url.strip()
        if validators.url(url):
            return url.strip()
        if url[0] == '/':
            return f'{self.base_url}{url}'.strip()
        if re.match(r'^\w+.*', url):
            return f'{parent_url}/{url}'.strip()

        return url

    def get_links_from_page(self, html_doc: BeautifulSoup, page_url: str) -> list[Link]:
        links: list[Link] = []
        for link in html_doc.findAll('a'):
            link_text = link.text.replace('\n', ' ').strip()
            link_url = self.format_url(link.get('href'), page_url)
            if self.is_url_valid(link_url):
                links.append(Link(link_text, link_url))
        return links

    def find_phone_numbers(self, html_doc: BeautifulSoup) -> list[PhoneNumber]:
        scripts = ' '.join(
            [script.text for script in html_doc.findAll('script')])
        text = html_doc.text + '\n' + scripts
        numbers_enumerator = phonenumbers.PhoneNumberMatcher(text, None)
        phone_number_list: list[PhoneNumber] = []

        for number in numbers_enumerator:
            escaped_number = PhoneNumber.escape_number(number.raw_string)
            headers = re.findall(rf'.*\s*:?\s*{escaped_number}', text)

            if len(headers) == 0:
                phone_number_list.append(PhoneNumber(number.raw_string, ''))
                continue

            for header in headers:
                header = re.sub(rf'({escaped_number})|([\t\n])', '', header)
                phone_number_list.append(
                    PhoneNumber(number.raw_string, header))

        return phone_number_list

    def get_page(self, url: str) -> BeautifulSoup:
        self.visited_urls.append(url)
        html_doc = HTTP.get(url, headers=HEADERS,
                            verify=True, allow_redirects=True).text
        html_doc_parsed = BeautifulSoup(html_doc, 'html.parser')
        return html_doc_parsed

    def filter_links(self, links: list[Link]) -> list[Link]:
        links = [link for link in links if link.normalized_text in PAGES_TO_CHECK and link.url not in self.visited_urls]
        return links

    def find_links_to_visit(self, html_doc: BeautifulSoup, page_url: str):
        links = self.get_links_from_page(html_doc, page_url)
        links = self.filter_links(links)
        links.sort(key=Link.comparer)
        self.links_to_visit.extend(links)

    def get_urls_to_visit(self):
        while self.last_visited_link < len(self.links_to_visit) - 1:
            self.last_visited_link += 1
            yield self.links_to_visit[self.last_visited_link].url

    def retrieve_main_phone_number(self) -> Optional[PhoneNumber]:
        for url in self.get_urls_to_visit():
            html_doc = self.get_page(url)
            phone_number_list = self.find_phone_numbers(html_doc)
            if len(phone_number_list) > 0:
                return PhoneNumber.get_main_phone_number(phone_number_list)
            self.find_links_to_visit(html_doc, url)
        return None


def get_url_from_args():
    if len(argv) < 2:
        raise Exception('You need to pass an URL to the program.')
    if not validators.url(argv[1]):
        raise Exception('You need to pass a correct URL to the program.')
    return argv[1]


if __name__ == '__main__':
    url = get_url_from_args()
    phone_number = WebPage(url).retrieve_main_phone_number()
    print(None if phone_number is None else phone_number.number)
