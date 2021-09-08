.. provable-test documentation master file, created by
   sphinx-quickstart on Wed Sep  8 13:28:25 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to provable-test's documentation!
=========================================

Provable-test is a simple project aiming to build a simple API returning USDT transactions
for a given address in a time frame.

How to run the webserver
========================
Provable-test requires:

- Python 3
- a valid API key for https://eth.getblock.io

Clone the repository and enter the created directory::

   git clone https://github.com/oliviera9/provable-test.git
   cd provable-test

Install Python dependencies (you may want to use a virtual environment)::

   pip install -r requirements.txt

Run the webserver with::

   export GETBLOCKIO_KEY=<API-KEY>
   python main.py

or::

   python main.py --key <API-KEY>

The webserver listens at port 3000 by default.
Pass option `--key <port>` to use a different port.

How to retrieve data
====================
Read API documentation at https://documenter.getpostman.com/view/11432526/U16jLQtp
