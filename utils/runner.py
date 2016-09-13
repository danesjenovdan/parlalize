import requests
from parlaposlanci.views import setMPStaticPL
from parlalize.settings import API_URL

def updateMPStatic():
    memberships = requests.get(API_URL+'/getMembersOfPGsRanges/').json()
    lastObject={"members":{}}
    print "[info] update MP static"
    for change in memberships:
        #call setters for new pg
        for pg in list(set(change["members"].keys())-set(lastObject["members"].keys())):
            for member in change["members"][pg]:
                setMPStaticPL(None, str(member), change["start_date"])

        #call setters for members which have change in memberships
        for pg in change["members"].keys():
            if pg in lastObject["members"].keys():
                for member in list(set(change["members"][pg])-set(lastObject["members"][pg])):
                    setMPStaticPL(None, str(member), change["start_date"])
        lastObject = change