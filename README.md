```
  _____  ______ _____               
 |  __ \|  ____/ ____|              
 | |__) | |__ | |       _ __  _   _ 
 |  _  /|  __|| |      | '_ \| | | |
 | | \ \| |   | |____ _| |_) | |_| |
 |_|  \_\_|    \_____(_) .__/ \__, |
                       | |     __/ |
                       |_|    |___/   v 2019.5.1
```

# RFC.py
-----

A simple python client that offers users the ability to search for, read and bookmark RFC's from the Internet Engineering Task Force whilst offline.


## Installation

Installation using pip is as simple as

```pip install RFC.py``` 

Alternatively, the repo can be cloned. See [here](#development) for more details.

The initial setup can take some time. See [Setup Process](#setup-process) for more details.

## Requirements 

**Python 3.6+ only**

See [requirements.txt](https://github.com/danielmichaels/RFC.py/blob/master/requirements.txt) for more details of what dependencies are required.

**Currently tested only on Linux**

specifically `Arch 4.17.x x86_64` but should work on most Linux systems.

## Demo

### Functionality

<p align="center">
    <img src="https://rawgit.com/danielmichaels/RFC.py/master/examples/demo.svg" alt="svg demo">
</p>


## Basic Usage
----

RFC.py runs in an interactive mode. It consists of a Home Page and three search options.

>> Home Page
>>  - Search by Number
>>  - Search by Keyword
>>  - Search through Bookmark
>>  - Latest 10 RFC's

**Search by Number**: The user can enter a valid RFC number

**Search by Keyword**: The user can enter a series of keywords to search. The keywords within the title of each RFC are checked. Multiple keywords can be queried at once.
Each result will list matching RFC's with their title and number, the user can then enter in the number they wish to view.

**Search through Bookmark**: If any bookmarks have been stored, this will output them to the terminal. The user can then view an RFC by entering its number.

**Latest 10 RFC's**: Returns the ten most recently added RFC's.

The IETF releases new RFC's each Sunday. The application will prompt the user once every 7 days if they wish to download the new RFC's to the database. This is optional.

### Setup Process

On the initial setup RFC.py will begin downloading the RFC's and write them to the database. This can take some time and is entirely dependent on the users connection.

- Total download ~ 175mb
- Database Size ~ 850mb

The root directory for database and configuration file is located on the users home path under `.rfc`. For example `~/.rfc`

## Running the tests

1. cd into the RFC.py site package root directory.
2. run ```python -m unittest -v```


## Development

If `RFC.py` is not installed via `pip install RFC.py` it can cloned and then be setup in the following ways:
1. **The preferred method**: change directory to `RFC.py` and run `pip install --editable .` which will download all the appropriate dependencies. It can now be run from the CLI as `rfc` or `python rfc.py`. It is *highly advisable* that the user do this within a virtual environment. This [post](http://click.pocoo.org/dev/setuptools/) gives a good reason why this method is preferred.
2. If you do not want to use `pip` then you can call the `rfc.py` module directly from the command line, but it may not be set correctly in the `PYTHONPATH`. If you see errors such as `ModuleNotFoundError: no module name 'rfcpy'` then you will need to set the path. Calling `export PYTHONPATH=.` from within the `RFC.py` folder will alleviate this error. More info at [Stack Overflow](https://stackoverflow.com/questions/338768/python-error-importerror-no-module-named).

## Meta

Daniel Michaels – https://www.danielms.site

Distributed under the MIT license. See [`LICENSE`](https://github.com/danielmichaels/RFC.py/blob/master/LICENSE.txt) for more information.

## Contributing

All requests, ideas or improvements are welcomed!

1. Fork it
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Inspired by

My desire to read RFC's whilst flying without Wifi.

