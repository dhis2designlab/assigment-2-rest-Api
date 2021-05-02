import  json
import os
import math

if __name__ == '__main__':
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "populationdata.json")
    data = json.load(open(json_url)) # data
    f = open("demofile2.json", "a")
    allData = []
    for c in data:
        countryCode = c["COUNTRYCODE"]
        countryName = c["COUNTRYNAME"]
        print(c ,"\n")
        for k,v in c.items():
            if k.strip() != "COUNTRYCODE" and k != "COUNTRYNAME":
                print("K: ", k, "v: ",v)
                if k and v:
                    data = {
                        "COUNTRYNAME": countryName,
                        "COUNTRYCODE": countryCode,
                        "YEAR": int(k),
                        "POP": int(v),
                    }
                print("data: ", data)
                allData.append(data)

    f.write(json.dumps(allData))
    f.close()


