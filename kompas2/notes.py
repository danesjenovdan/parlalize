import requests
import numpy as np
import matplotlib.pyplot as plt

# kako prikazati kompas

def showCompass():

    fig, ax = plt.subplots()
    ax.scatter(ideology, zeros)
    for i, txt in enumerate(people):
        ax.annotate(str(txt), (ideology[i], zeros[i]))
    plt.show()

    return false

def assignValueToOption(option):
    if option == 'ni':
        return 0
    if option == 'za':
        return 1
    if option == 'proti':
        return 2
    if option == 'kvorum':
        return 3
    if option == 'ni obstajal':
        return 5

def getData():
    allballots = requests.get('https://data.parlameter.si/v1/getAllBallots/').json()
    people = requests.get('https://data.parlameter.si/v1/getMPs/').json()
    people_ids = sorted([person['id'] for person in people])
    people_ballots = []
    for voter in people_ids:
        people_ballots.append([ballot for ballot in allballots if ballot['voter'] == voter])
    lengths = [len(person) for person in people_ballots]
    all_vote_ids = []

    all_vote_ids = []
    for person in people_ballots:
        for ballot in person:
            all_vote_ids.append(ballot['vote'])
    all_vote_ids = set(all_vote_ids)

    for person in people_ballots:
        if len(person) < max(lengths):
            for vote_id in all_vote_ids:
                if vote_id not in [ballot['vote'] for ballot in person]:
                    person.append({'vote': vote_id, 'voter': person[0]['id'], 'option': 'ni obstajal', 'id': 666})

    people_ballots_sorted = sorted([sorted(person, key=lambda k: k['vote']) for person in people_ballots], key=lambda j: j[0]['voter'])

    people_ballots_sorted_list = [person for person in people_ballots_sorted]

    for i, person in enumerate(people_ballots_sorted_list):
        for j, ballot in enumerate(person):
            people_ballots_sorted_list[i][j] = assignValueToOption(ballot['option'])

    return people_ids, people_ballots_sorted, people_ballots_sorted_list
