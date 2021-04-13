import flask, json
import os
from flask import request, jsonify
import requests

app = flask.Flask(__name__)
app.config["DEBUG"] = True

if __name__ == '__main__':
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "who.json")
    data = json.load(open(json_url)) # data

@app.route('/', methods=['GET'])
def home():
    response = jsonify(message="Simple server is running")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/api/dimension', methods=['GET'])
def getDimension():
    query_parameters = request.args
    curr_data = data["dimension"]
    page = query_parameters.get('page', type = int)
    response = curr_data
    
    args = [i for i in query_parameters.keys()]
    for arg in args:
        if arg != "page":
            param = query_parameters.get(arg) # get value given with the arg
            response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
            curr_data = response # update data

            # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
    if page:
        element_per_page = 10
        response = list(response)[element_per_page * (page - 1): ] # skip elements based on page provided
    response = jsonify(response)

    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    
    return response, 200



@app.route('/api/fact', methods=['GET'])
def getFact():
    query_parameters = request.args
    curr_data = data["fact"]
    response = curr_data
    page = query_parameters.get('page', type = int)

    args = [i for i in query_parameters.keys()]
    print(args)
    for arg in args:
        if arg != "page":
            param = query_parameters.get(arg) # get value given with the arg
            response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
            curr_data = response # update data

            # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
    if page:
        element_per_page = 10
        response = list(response)[element_per_page * (page - 1): ] # skip elements based on page provided
    response = jsonify(response)

    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    
    return response, 200

@app.route('/api', methods=['GET'])
def getAPI():
    query_parameters = request.args
    curr_data = data["fact"]
    response = data
    page = query_parameters.get('page', type = int)

    args = [i for i in query_parameters.keys()]
    for arg in args:
        if arg != "page":
            param = query_parameters.get(arg) # get value given with the arg
            response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
            curr_data = response # update data

            # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
    if page:
        element_per_page = 10
        response = list(response)[element_per_page * (page - 1): ] # skip elements based on page provided
    response = jsonify(response)

    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    
    return response, 200

app.run()