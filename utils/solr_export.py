import requests
import json
from parlaseje.models import Speech
from datetime import datetime

SOLR_URL = 'http://127.0.0.1:8983/solr/parlasearch'


def exportSpeeches():

    # get all valid speeches
    speeches = Speech.getValidSpeeches(datetime.now())

    # get all ids from solr
    a = requests.get(SOLR_URL + "/select?wt=json&q=id:*&fl=id&rows=100000000")
    indexes = a.json()["response"]["docs"]

    # find ids of speeches and remove g from begining of id string
    idsInSolr = [int(line["id"].replace('g', ''))
                 for line
                 in indexes if "g" in line["id"]]

    i = 0

    for speech in speeches.exclude(id__in=idsInSolr):
        output = [{
            'id': 'g' + str(speech.id_parladata),
            'speaker_i': speech.person.first().id_parladata,
            'session_i': speech.session.id_parladata,
            'org_i': speech.session.organization.id,
            'party_i': speech.organization.id_parladata,
            'datetime_dt': speech.start_time.isoformat(),
            'content_t': speech.content,
            'tip_t': 'govor',
            'the_order': speech.the_order
        }]

        output = json.dumps(output)

        if i % 100 == 0:
            url = SOLR_URL + '/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})


        else:
            r = requests.post(SOLR_URL + '/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1

def deleteNonValidSpeeches():
    # get all ids from solr
    a = requests.get(SOLR_URL + "/select?wt=json&q=id:*&fl=id&rows=100000000")
    indexes = a.json()["response"]["docs"]

        # find ids of speeches and remove g from begining of id string
    idsInSolr = [int(line["id"].replace('g', ''))
                 for line
                 in indexes if "g" in line["id"]]

    # get all valid speeches
    validSpeeches = Speech.getValidSpeeches(datetime.now())
    idsInData = validSpeeches.values_list("id_parladata", flat=True)

    # find ids of speeches in solr for delete
    idsForDelete = list(set(idsInSolr) - set(idsInData))
    idsForDelete = ['g'+str(gid) for gid in idsForDelete]

    # prepare query data
    data = {'delete': idsForDelete
            }

    r = requests.post(SOLR_URL + '/update?commit=true',
                      data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})

    print r.text

    return


def deleteSpeeches():
    a = requests.get(SOLR_URL + "/select?wt=json&q=id:*&fl=id&fq=tip_t:govor&rows=100000000")
    indexes = a.json()["response"]["docs"]
    idsForDelete = [idx['id'] for idx in indexes]
    data = {'delete': idsForDelete
            }

    r = requests.post(SOLR_URL + '/update?commit=true',
                      data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})

    print r.text
    return True

def deleteSessions():
    a = requests.get(SOLR_URL + "/select?wt=json&q=id:*&fl=id&fq=tip_t:seja&rows=100000000")
    indexes = a.json()["response"]["docs"]
    idsForDelete = [idx['id'] for idx in indexes]
    data = {'delete': idsForDelete
            }

    r = requests.post(SOLR_URL + '/update?commit=true',
                      data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})

    print r.text
    return True