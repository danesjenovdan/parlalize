import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from sklearn.decomposition import PCA as sklearnPCA
from sklearn.manifold import MDS as sklearnMDS

matplotlib.rc('font', family='Arial')

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

def getPeoplesNames(ids):
    names_list = []
    for person_id in ids:
        print person_id
        data = requests.get('https://analize.parlameter.si/v1/p/getMPStatic/' + str(person_id) + '/').json()
        name = data['person']['name']

        names_list.append(data['person']['name'])

    return names_list

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

    thearray = np.array(people_ballots_sorted_list)

    sklearn_pca = sklearnPCA(n_components=2)
    sklearn_transf = sklearn_pca.fit_transform(thearray)

    fig, ax = plt.subplots()
    ax.scatter(sklearn_transf[0:90,0],sklearn_transf[0:90,1])#, 'o', markersize=7, color='blue', alpha=0.5)
    for i, txt in enumerate(people_ids):
        ax.annotate(str(txt), (sklearn_transf[0:90,0][i], sklearn_transf[0:90,1][i]))

    # plt.plot(sklearn_transf[0:90,0],sklearn_transf[0:90,1], 'o', markersize=7, color='blue', alpha=0.5)
    plt.savefig('PCA.png')

    sklearn_mda = sklearnMDS(n_components=2, metric=True, max_iter=3000, verbose=1, n_jobs=-2, dissimilarity='euclidean')
    mda_result = sklearn_mda.fit_transform(people_ballots_sorted_list)

    fig2, ax2 = plt.subplots()
    ax2.scatter(mda_result[0:90, 0], mda_result[0:90, 1])
    for i, txt in enumerate(getPeoplesNames(people_ids)):
        ax2.annotate(str(txt), (mda_result[0:90, 0][i], mda_result[0:90, 1][i]))
    plt.savefig('MDA.png')

    return people_ids, people_ballots_sorted, people_ballots_sorted_list, sklearn_mda
