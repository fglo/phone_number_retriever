from sys import argv
import validators
from scrape import WebPage


def get_urls_from_args():
    if len(argv) < 2:
        raise Exception('You need to pass an URL to the program.')
    while len(argv) >= 2:
        if not validators.url(argv[1]):
            raise Exception('You need to pass a correct URL to the program.')
        yield argv.pop(1)


if __name__ == '__main__':
    for url in get_urls_from_args():
        phonenumber = WebPage(url).retrieve_main_phone_number()
        print(None if phonenumber is None else phonenumber.number)
