import flask, json
import os
from flask import request, jsonify
import requests

app = flask.Flask(__name__)
app.config["DEBUG"] = True

keyParam = ["page", "sort", "limit", "order"] # pagination, sort, filtering

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
    response = curr_data
    
    args = [i for i in query_parameters.keys()]
    for arg in args:
        if arg not in keyParam:
            param = query_parameters.get(arg) # get value given with the arg
            response = [c for c in curr_data if c[arg] in param] # get all data that matches
            curr_data = response # update data

    # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
    response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
    response = jsonify(response) 
    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    
    return response, 200



@app.route('/api/fact', methods=['GET'])
def getFact():
    query_parameters = request.args
    curr_data = data["fact"]
    response = curr_data

    args = [i for i in query_parameters.keys()]
    print(args)
    for arg in args:
        if arg not in keyParam:
            param = query_parameters.get(arg) # get value given with the arg
            response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
            curr_data = response # update data

    # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
    response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
    response = jsonify(response) 

    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    
    return response, 200

@app.route('/api', methods=['GET'])
def getAPI():
    query_parameters = request.args
    curr_data = data["fact"]
    response = data
    

    args = [i for i in query_parameters.keys()]
    for arg in args:
        if arg not in keyParam:
            param = query_parameters.get(arg) # get value given with the arg
            response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
            curr_data = response # update data
            # filtering numbers? e.g ?value=20-50

    # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
    response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
    response = jsonify(response) 

    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    
    return response, 200


# Filtering, sorting, pagination
def applyAllKeyParam(query_parameters, response):
    limit = query_parameters.get('limit', type = int)
    page = query_parameters.get('page', type = int)
    sort = query_parameters.get('sort')
    order = query_parameters.get('order', default="asc")
    filtering = query_parameters.get('filtering', type = int)
    
    
    isDescending = False if order == "asc" else True
    if sort:
        bits = sort.split(",")
        response = sorted(response, key=lambda x : ([x["dims"][key.upper()] for key in bits if key.upper() != "VALUE"]), reverse=isDescending)
        if "value" in bits:
            response = sorted(response, key=lambda x : x["VALUE"], reverse=isDescending)

    if page:
        element_per_page = 10
        if limit:
            element_per_page = limit
        
        start = element_per_page * (page - 1) # start index
        end = start + element_per_page # end index

        if page == 1: # if its the first page
            end = element_per_page # define end as 10 
        response = list(response)[start: end] # skip elements based on page provided

    elif limit:
        response = list(response)[:limit] # override value

    return response
    

app.run()