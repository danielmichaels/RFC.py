import sys

import click
import logging
import requests
import subprocess

from rfcpy.utils import get_text

logging.basicConfig(level=logging.INFO)


@click.command()
@click.argument('rfc_number')
def main(rfc_number: str):
    """
    A simple IETF Request For Comments (RFC) command line utiity
    Provide the RFC number you wish to view in the terminal as an
    argument.

    Examples:

    python cli.py 8305 --> WILL WORK

    python cli.py <anything other than digits --> WILL FAIL

    If the RFC exists it will be displayed using unix's LESS program.
    """
    try:
        title, body = get_rfc(rfc_number)
        output = printer(title, body)
        less(output)
    except TypeError as error:
        logging.error(f'{error} raised on rfc_number: {rfc_number}')
        print('Error was raised most likely indicating this RFC is not '
              'in existence, please check the number before trying again.')
    except AttributeError as error:
        logging.error(f'{error} raised on rfc_number: {rfc_number}')
        print(f'Error was raised on rfc_number:{rfc_number} this is '
              'often caused by RFCs that do not exist or are formatted '
              'poorly.')
    except requests.ConnectionError as e:
        logging.error(e)
        print('ConnectionError raised, please check your connection!')


def get_rfc(rfc_number: str):
    """The driver that powers the downloading of RFC text. The user must enter
    a valid RFC using only integer's [0-9]. RFC's are retrieved in HTML format
    parsed using BeautifulSoup utility functions.

    :arg rfc_number: str(integer) from command line argument
    :return title and body text from RFC's response.
    """
    if not rfc_number.isdigit():
        print('[*]>>>ERROR<<<[*]')
        print('Please enter only integers [0-9] and run script again!')
        sys.exit(1)
    url = f"https://tools.ietf.org/html/rfc{rfc_number}"
    resp = requests.get(url)
    if resp.status_code == 200:
        text = resp.text
        title = None
        body = get_text(text)
        return title, body


def printer(title: str, body: str):
    """Return the title and body of RFC as bytecode."""
    output = (f"""
    {title}
    
    {body.strip()}
    """)
    echo = subprocess.check_output(('echo', output)).strip()
    return echo


def less(data: bytes):
    """Display the RFC in terminal using unix's LESS program."""
    process = subprocess.Popen(["less", "-rn"], stdin=subprocess.PIPE)

    try:
        process.stdin.write(data)
        process.communicate()
    except IOError as e:
        logging.error(f'The following error propagated in function(less): {e}')
        raise


if __name__ == '__main__':
    main()
