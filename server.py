#!/usr/bin/env python3
import os
import sys
import json
import random
import os.path
import yaml

from flask import Flask
from flask import request
from flask import send_from_directory

from two1.wallet import Wallet
from two1.bitserv.flask import Payment

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)

# Print error and die if a files directory isn't provided
if len(sys.argv) != 2:
    print("Usage: {} <files_directory>".format(sys.argv[0]))
    sys.exit(1)

dir_path = os.path.abspath(sys.argv[1])

# get a list of the files in the directory
file_list = os.listdir(dir_path)

# simple content model: dictionary of files w/ prices
files = {}
for file_id in range(len(file_list)):
    files[file_id+1] = file_list[file_id], random.randrange(25000, 25001)

@app.route('/')
def hello():
    return 'It doesnt work yet!'

@app.route('/manifest')
def docs():
    '''
    Serves the app manifest to the 21 crawler.
    '''
    with open('manifest.yaml', 'r') as f:
        manifest_yaml = yaml.load(f)
    return json.dumps(manifest_yaml)

# endpoint to look up files to buy
@app.route('/files')
def file_lookup():
    return json.dumps(files)

@app.route('/client')
def client():
    '''
    Provides an example client script.
    '''
    return send_from_directory('static', 'client.py')

# return the price of the selected file
def get_price_from_request(request):
    id = int(request.args.get('selection'))
    return files[id][1]


# machine-payable endpoint that returns selected file if payment made
@app.route('/buy')
@payment.required(get_price_from_request)
def buy_file():

    # extract selection from client request
    sel = int(request.args.get('selection'))

    # check if selection is valid
    if(sel < 1 or sel > len(file_list)):
        return 'Invalid selection.'
    else:
        return send_from_directory(dir_path, file_list[int(sel)-1])

if __name__ == '__main__':
	app.run(host='<your_ip_address>')
