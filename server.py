# -*- coding: utf-8 -*-
import flask, json
import os
import math
from flask import request, jsonify
import requests
from flask import render_template

app = flask.Flask(__name__)
# app.config["DEBUG"] = True
keyParam = {"search", "page", "paging", "sort", "pageSize", "order"} # pagination, sort, filtering


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "populationdata.json")
data = json.load(open(json_url, encoding='utf-8')) # data

class BadRequest(Exception):
    """Custom exception class to be thrown when local error occurs."""
    def __init__(self, message, status=400, payload=None):
        self.message = message
        self.status = status
        self.payload = payload


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    """Catch BadRequest exception globally, serialize into JSON, and respond with 400."""
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 400

@app.errorhandler(500)
def internal_server_error(e):
    # note that we set the 500 status explicitly
    return render_template('500.html'), 500


@app.route('/', methods=['GET'])
def home():
    response = jsonify(message="Simple server is running")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/api', methods=['GET'])
def getAPIpop():
    query_parameters = request.args
    curr_data = data
    response = curr_data
    allowedFilterParams = {"population" : "Population", "populationmale" : "PopulationMale", "populationfemale" : "PopulationFemale"}
    try:
        args = [i for i in query_parameters.keys()]
        for arg in args:
            if arg not in keyParam:
                param = query_parameters.get(arg) # get value given with the arg
                print("param: ", param,  "\n\n")
                print("arg: ", arg, "lower: ", arg.lower(), "\n\n")
                if arg.lower() in allowedFilterParams:
                    valueBits = param.split("-")
                    queriedProperty = allowedFilterParams[arg.lower()]
                    print("\n\n------dsd: ", queriedProperty)
                    if len(valueBits) == 1: # should not be more than two value?
                        response = [c for c in curr_data if int(c[queriedProperty]) == int(param)] # get all data that matches
                    elif len(valueBits) == 2: # should not be more than two value?
                        left = int(valueBits[0])
                        right = int(valueBits[1])
                        response = [c for c in curr_data if int(c[queriedProperty]) >= left and int(c[queriedProperty]) <= right] # get all data that matches
                else:
                    response = [c for c in curr_data if c[arg] in param] # get all data that matches
                curr_data = response # update data
                # filtering numbers? e.g ?value=20-50

        # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
        response = applyAllKeyParam(query_parameters, response) # apply filtering, sorting and pagiantion
        response = jsonify(response) 

        # Enable Access-Control-Allow-Origin
        response.headers.add("Access-Control-Allow-Origin", "*")
        
        return response, 200
    except Exception as e:
        raise BadRequest(e)

# Filtering, sorting, pagination
def applyAllKeyParam(query_parameters, response):
    pageSize = query_parameters.get('pageSize', type = int)
    page = query_parameters.get('page', type = int, default=1)
    paging = query_parameters.get('paging', type = str, default=True)
    sort = query_parameters.get('sort')
    order = query_parameters.get('order', default="asc")
    filtering = query_parameters.get('filtering', type = int)
    search = query_parameters.get('search', type = str)
    
    element_per_page = len(response) # default element per page if pagination is not queried.
    pageCount = 1

    
    if search:
        # TODO:
        print("")

    totalElements =  len(response)
    isDescending = False if order == "asc" else True
    if sort:
        bits = sort.split(",")
        response = sorted(response, key=lambda x : ([x[key.upper()] for key in bits if key.upper() != "VALUE"]), reverse=isDescending)
        if "pop" in bits:
            response = sorted(response, key=lambda x : x["POP"], reverse=isDescending)
    
    isPaging  = True if paging != "False" else False
    print("isPaging ", isPaging)
    if isPaging:
        element_per_page = 10
        if page:
            if pageSize:
                element_per_page = pageSize
            start = element_per_page * (page - 1) # start index
            end = start + element_per_page # end index

            if page == 1: # if its the first page
                end = element_per_page # define end as the first pageSize is
            response = list(response)[start: end] # skip elements based on page provided

        elif pageSize:
            response = list(response)[:pageSize] # override value
        
        pageCount = math.ceil(totalElements / element_per_page)
        if totalElements <= element_per_page:
            pageCount = 1
    
    
    pageObject = {"page" : page, "pageSize" : element_per_page, "pageCount": pageCount, "results": len(response) }

    return {"page" : pageObject, "results": response}

if __name__ == "__main__":
    app.register_error_handler(500, internal_server_error)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)))





# @app.route('/api/dimension', methods=['GET'])
# def getDimension():
#     query_parameters = request.args
#     curr_data = data["dimension"]
#     response = curr_data
    
#     args = [i for i in query_parameters.keys()]
#     for arg in args:
#         if arg not in keyParam:
#             param = query_parameters.get(arg) # get value given with the arg
#             response = [c for c in curr_data if c[arg] in param] # get all data that matches
#             curr_data = response # update data

#     # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
#     response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
#     response = jsonify(response) 
#     # Enable Access-Control-Allow-Origin
#     response.headers.add("Access-Control-Allow-Origin", "*")
    
#     return response, 200


# @app.route('/api/fact', methods=['GET'])
# def getFact():
#     query_parameters = request.args
#     curr_data = data["fact"]
#     response = curr_data

#     args = [i for i in query_parameters.keys()]
#     print(args)
#     for arg in args:
#         if arg not in keyParam:
#             param = query_parameters.get(arg) # get value given with the arg
#             if arg.lower() == "value":
#                 valueBits = param.split("-")
#                 print("DD",valueBits)
#                 if len(valueBits) == 1: # should not be more than two value?
#                     response = [c for c in curr_data if int(c["VALUE"]) == int(param)] # get all data that matches
#                 if len(valueBits) == 2: # should not be more than two value?
#                     left = int(valueBits[0])
#                     right = int(valueBits[1])
#                     print("valuebits ", left, right)
#                     response = [c for c in curr_data if int(c["VALUE"]) >= left and int(c["VALUE"]) <= right] # get all data that matches
#             else:
#                 response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
#             curr_data = response # update data

#     # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
#     response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
#     response = jsonify(response) 

#     # Enable Access-Control-Allow-Origin
#     response.headers.add("Access-Control-Allow-Origin", "*")
    
#     return response, 200

# @app.route('/api', methods=['GET'])
# def getAPI():
#     query_parameters = request.args
#     # curr_data = data["fact"]
#     curr_data = data
#     response = curr_data
    

#     args = [i for i in query_parameters.keys()]
#     for arg in args:
#         if arg not in keyParam:
#             param = query_parameters.get(arg) # get value given with the arg
#             if arg.lower() == "value":
#                 valueBits = param.split("-")
#                 print("DD",valueBits)
#                 if len(valueBits) == 1: # should not be more than two value?
#                     response = [c for c in curr_data if int(c["VALUE"]) == int(param)] # get all data that matches
#                 if len(valueBits) == 2: # should not be more than two value?
#                     left = int(valueBits[0])
#                     right = int(valueBits[1])
#                     print("valuebits ", left, right)
#                     response = [c for c in curr_data if int(c["VALUE"]) >= left and int(c["VALUE"]) <= right] # get all data that matches
#             else:
#                 response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
#             curr_data = response # update data
#             # filtering numbers? e.g ?value=20-50

#     # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
#     response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
#     response = jsonify(response) 

#     # Enable Access-Control-Allow-Origin
#     response.headers.add("Access-Control-Allow-Origin", "*")
    
#     return response, 200
# -*- coding: utf-8 -*-
import flask, json
import os
import math
from flask import request, jsonify
import requests
from flask import render_template

app = flask.Flask(__name__)
# app.config["DEBUG"] = True
keyParam = {"search", "page", "paging", "sort", "pageSize", "order"} # pagination, sort, filtering


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "populationdata.json")
data = json.load(open(json_url, encoding='utf-8')) # data

class BadRequest(Exception):
    """Custom exception class to be thrown when local error occurs."""
    def __init__(self, message, status=400, payload=None):
        self.message = message
        self.status = status
        self.payload = payload


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    """Catch BadRequest exception globally, serialize into JSON, and respond with 400."""
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 400

@app.errorhandler(500)
def internal_server_error(e):
    # note that we set the 500 status explicitly
    return render_template('500.html'), 500


@app.route('/', methods=['GET'])
def home():
    response = jsonify(message="Simple server is running")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/api', methods=['GET'])
def getAPIpop():
    query_parameters = request.args
    curr_data = data
    response = curr_data
    allowedFilterParams = {"population" : "Population", "populationmale" : "PopulationMale", "populationfemale" : "PopulationFemale"}
    try:
        args = [i for i in query_parameters.keys()]
        for arg in args:
            if arg not in keyParam:
                param = query_parameters.get(arg) # get value given with the arg
                print("param: ", param,  "\n\n")
                print("arg: ", arg, "lower: ", arg.lower(), "\n\n")
                if arg.lower() in allowedFilterParams:
                    valueBits = param.split("-")
                    queriedProperty = allowedFilterParams[arg.lower()]
                    print("\n\n------dsd: ", queriedProperty)
                    if len(valueBits) == 1: # should not be more than two value?
                        response = [c for c in curr_data if int(c[queriedProperty]) == int(param)] # get all data that matches
                    elif len(valueBits) == 2: # should not be more than two value?
                        left = int(valueBits[0])
                        right = int(valueBits[1])
                        response = [c for c in curr_data if int(c[queriedProperty]) >= left and int(c[queriedProperty]) <= right] # get all data that matches
                else:
                    response = [c for c in curr_data if c[arg] in param] # get all data that matches
                curr_data = response # update data
                # filtering numbers? e.g ?value=20-50

        # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
        response = applyAllKeyParam(query_parameters, response) # apply filtering, sorting and pagiantion
        response = jsonify(response) 

        # Enable Access-Control-Allow-Origin
        response.headers.add("Access-Control-Allow-Origin", "*")
        
        return response, 200
    except Exception as e:
        raise BadRequest(e)

# Filtering, sorting, pagination
def applyAllKeyParam(query_parameters, response):
    pageSize = query_parameters.get('pageSize', type = int)
    page = query_parameters.get('page', type = int, default=1)
    paging = query_parameters.get('paging', type = str, default=True)
    sort = query_parameters.get('sort')
    order = query_parameters.get('order', default="asc")
    filtering = query_parameters.get('filtering', type = int)
    search = query_parameters.get('search', type = str)
    
    element_per_page = len(response) # default element per page if pagination is not queried.
    pageCount = 1

    
    if search:
        # TODO:
        print("")

    totalElements =  len(response)
    isDescending = False if order == "asc" else True
    if sort:
        bits = sort.split(",")
        response = sorted(response, key=lambda x : ([x[key.upper()] for key in bits if key.upper() != "VALUE"]), reverse=isDescending)
        if "pop" in bits:
            response = sorted(response, key=lambda x : x["POP"], reverse=isDescending)
    
    isPaging  = True if paging != "False" else False
    print("isPaging ", isPaging)
    if isPaging:
        element_per_page = 10
        if page:
            if pageSize:
                element_per_page = pageSize
            start = element_per_page * (page - 1) # start index
            end = start + element_per_page # end index

            if page == 1: # if its the first page
                end = element_per_page # define end as the first pageSize is
            response = list(response)[start: end] # skip elements based on page provided

        elif pageSize:
            response = list(response)[:pageSize] # override value
        
        pageCount = math.ceil(totalElements / element_per_page)
        if totalElements <= element_per_page:
            pageCount = 1
    
    
    pageObject = {"page" : page, "pageSize" : element_per_page, "pageCount": pageCount, "results": len(response) }

    return {"page" : pageObject, "results": response}

if __name__ == "__main__":
    app.register_error_handler(500, internal_server_error)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)))





# @app.route('/api/dimension', methods=['GET'])
# def getDimension():
#     query_parameters = request.args
#     curr_data = data["dimension"]
#     response = curr_data
    
#     args = [i for i in query_parameters.keys()]
#     for arg in args:
#         if arg not in keyParam:
#             param = query_parameters.get(arg) # get value given with the arg
#             response = [c for c in curr_data if c[arg] in param] # get all data that matches
#             curr_data = response # update data

#     # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
#     response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
#     response = jsonify(response) 
#     # Enable Access-Control-Allow-Origin
#     response.headers.add("Access-Control-Allow-Origin", "*")
    
#     return response, 200


# @app.route('/api/fact', methods=['GET'])
# def getFact():
#     query_parameters = request.args
#     curr_data = data["fact"]
#     response = curr_data

#     args = [i for i in query_parameters.keys()]
#     print(args)
#     for arg in args:
#         if arg not in keyParam:
#             param = query_parameters.get(arg) # get value given with the arg
#             if arg.lower() == "value":
#                 valueBits = param.split("-")
#                 print("DD",valueBits)
#                 if len(valueBits) == 1: # should not be more than two value?
#                     response = [c for c in curr_data if int(c["VALUE"]) == int(param)] # get all data that matches
#                 if len(valueBits) == 2: # should not be more than two value?
#                     left = int(valueBits[0])
#                     right = int(valueBits[1])
#                     print("valuebits ", left, right)
#                     response = [c for c in curr_data if int(c["VALUE"]) >= left and int(c["VALUE"]) <= right] # get all data that matches
#             else:
#                 response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
#             curr_data = response # update data

#     # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
#     response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
#     response = jsonify(response) 

#     # Enable Access-Control-Allow-Origin
#     response.headers.add("Access-Control-Allow-Origin", "*")
    
#     return response, 200

# @app.route('/api', methods=['GET'])
# def getAPI():
#     query_parameters = request.args
#     # curr_data = data["fact"]
#     curr_data = data
#     response = curr_data
    

#     args = [i for i in query_parameters.keys()]
#     for arg in args:
#         if arg not in keyParam:
#             param = query_parameters.get(arg) # get value given with the arg
#             if arg.lower() == "value":
#                 valueBits = param.split("-")
#                 print("DD",valueBits)
#                 if len(valueBits) == 1: # should not be more than two value?
#                     response = [c for c in curr_data if int(c["VALUE"]) == int(param)] # get all data that matches
#                 if len(valueBits) == 2: # should not be more than two value?
#                     left = int(valueBits[0])
#                     right = int(valueBits[1])
#                     print("valuebits ", left, right)
#                     response = [c for c in curr_data if int(c["VALUE"]) >= left and int(c["VALUE"]) <= right] # get all data that matches
#             else:
#                 response = [c for c in curr_data if c["dims"][arg.upper()] in param] # get all data that matches
#             curr_data = response # update data
#             # filtering numbers? e.g ?value=20-50

#     # Paginating – For example, ?page=2, ?p=2 or viewItems=10-30
#     response = applyAllKeyParam(query_parameters, response) # apply advanced filtering, sorting and pagiantion
#     response = jsonify(response) 

#     # Enable Access-Control-Allow-Origin
#     response.headers.add("Access-Control-Allow-Origin", "*")
    
#     return response, 200
