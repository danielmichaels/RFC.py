```
  _____  ______ _____               
 |  __ \|  ____/ ____|              
 | |__) | |__ | |       _ __  _   _ 
 |  _  /|  __|| |      | '_ \| | | |
 | | \ \| |   | |____ _| |_) | |_| |
 |_|  \_\_|    \_____(_) .__/ \__, |
                       | |     __/ |
                       |_|    |___/   v 1.0
```

# RFC.py
-----

A simple python client that offers users the ability to search for, read and bookmark RFC's from the Internet Engineering Task Force whilst offline.


## Installation

Installation using pip is as simple as

```pip install rfc.py``` **COMING SOON**

Or clone this repo and run like so

```shell
cd rfc
python rfc.py
```

**Python 3.6+ only**

See [requirements.txt]() for more details of what dependencies are required.

## Demo

<p align="center">
    <img src="https://cdn.rawgit.com/danielmichaels/rfc.py/examples/basic_usage.svg" alt="svg demo">
</p>

## Basic Usage
----

RFC.py runs in an interactive mode. It consists of a Home Page and three search options.

>> Home Page
>>  - Search by Number
>>  - Search by Keyword
>>  - Search by Bookmark

**Search by Number**: The user can enter a valid RFC number

**Search by Keyword**: The user can enter a series of keywords to search. The keywords are only check within the title of each RFC. 
Each result will list matching RFC's with their title and number, the user can then enter in the number they wish to view.

**Search by Bookmark**: If any bookmarks have been stored, this will output them to the terminal. The user can then view an RFC by entering its number.

The IETF releases new RFC's each Sunday. RFC.py will prompt the user once every 7 days if they wish to download the new RFC's to the database. This is optional and by pressing [Enter] will default to No.

### Setup Process

On the initial setup RFC.py will begin downloading the RFC's and write them to the database. This can take some time and is entirely dependant on the users connection.

- Total download ~ 175mb
- Database Size ~ 850mb

## Running the tests

1. cd into the rfc.py site package root directory.
2. run ```python -m unittest -v```

## Meta

Daniel Michaels – https://www.danielms.site

Distributed under the MIT license. See ``LICENSE`` for more information.

## Contributing

All requests, ideas or improvements are welcomed!

1. Fork it
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Inspired by..

My desire to read RFC's whilst flying without Wifi.