import requests
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA as sklearnPCA
from sklearn.manifold import MDS as sklearnMDS

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
        data = requests.get('https://analize.parlameter.si/v1/p/getMPStatic/' + str(person_id) + '/').json()
        name = data['person']['name']

        names_list.append(data['person']['name'].encode('ascii', errors='xmlcharrefreplace'))

    return names_list

def makeSimilarities(people_ballots_sorted_list):

    similarities = []

    # iterate through people
    for i, personA in enumerate(people_ballots_sorted_list):
        similarities.append([])

        # iterate through people for a second time
        for j, personB in enumerate(people_ballots_sorted_list):

            # start counting similar ballots
            ballot_similarity = 0
            for k, ballot in enumerate(personA):
                if ballot == personB[k]:
                    ballot_similarity = ballot_similarity + 1

            # done comparing with person
            similarities[i].append(ballot_similarity)

    return np.array(similarities)

def createCompassDict(vT, people, people_ids):
    jsondata = []
    attendance_list = getAttendanceData(people_ids)
    vocabularysize_list = getVocabularySizeData(people_ids)
    numberofspokenwords_list = getNumberOfSpokenWordsData(people_ids)
    problematicno_list, privzdignjeno_list, preprosto_list = getStyleScoresData(people_ids)

    for i, person_id in enumerate(people_ids):
        jsondata.append({
            'id': person_id,
            'name': (person['name'] for person in people if person['id'] == person_id).next(),
            'acronym': (person['acronym'] for person in people if person['id'] == person_id).next(),
            'ideology': vT[1,i],
            'ideology*': vT[0,i],
            'attendance': attendance_list[i],
            'vocabularysize': vocabularysize_list[i],
            'numberofspokenwords': numberofspokenwords_list[i],
            'problematicno': problematicno_list[i],
            'privzdignjeno': privzdignjeno_list[i],
            'preprosto': preprosto_list[i]
        })

    return jsondata

def getAttendanceData(people_ids):
    attendance_list = []
    for person_id in people_ids:
        print person_id
        data = requests.get('https://analize.parlameter.si/v1/p/getPresence/' + str(person_id)).json()
        attendance_list.append(data['results']['value'])

    return attendance_list

def getVocabularySizeData(people_ids):
    vocabularysize_list = []
    for person_id in people_ids:
        print person_id
        data = requests.get('https://analize.parlameter.si/v1/p/getVocabularySize/' + str(person_id)).json()
        vocabularysize_list.append(data['results']['value'])

    return vocabularysize_list

def getNumberOfSpokenWordsData(people_ids):
    numberofspokenwords_list = []
    for person_id in people_ids:
        print person_id
        data = requests.get('https://analize.parlameter.si/v1/p/getNumberOfSpokenWords/' + str(person_id)).json()
        numberofspokenwords_list.append(data['results']['value'])

    return numberofspokenwords_list

def getStyleScoresData(people_ids):
    problematicno_list = []
    privzdignjeno_list = []
    preprosto_list = []
    for person_id in people_ids:
        print person_id
        data = requests.get('https://analize.parlameter.si/v1/p/getStyleScores/' + str(person_id)).json()
        problematicno_list.append(data['results']['problematicno'])
        privzdignjeno_list.append(data['results']['privzdignjeno'])
        preprosto_list.append(data['results']['preprosto'])

    return problematicno_list, privzdignjeno_list, preprosto_list

def getData():
    allballots = requests.get('https://data.parlameter.si/v1/getAllBallots/').json()
    people = requests.get('https://data.parlameter.si/v1/getMPs/').json()
    people_ids = sorted([person['id'] for person in people])
    people_ballots = []
    for voter in people_ids:
        people_ballots.append([ballot for ballot in allballots if ballot['voter'] == voter])
    lengths = [len(person) for person in people_ballots]
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

    people_names = getPeoplesNames(people_ids)

    # sklearn_pca = sklearnPCA(n_components=2)
    # sklearn_transf = sklearn_pca.fit_transform(thearray)
    #
    # fig, ax = plt.subplots()
    # ax.scatter(sklearn_transf[0:90,0],sklearn_transf[0:90,1])#, 'o', markersize=7, color='blue', alpha=0.5)
    # for i, txt in enumerate(people_ids):
    #     ax.annotate(str(txt), (sklearn_transf[0:90,0][i], sklearn_transf[0:90,1][i]))
    #
    # # plt.plot(sklearn_transf[0:90,0],sklearn_transf[0:90,1], 'o', markersize=7, color='blue', alpha=0.5)
    # plt.savefig('PCA.png')
    #
    # sklearn_mda = sklearnMDS(n_components=2, metric=True, max_iter=3000, verbose=1, n_jobs=-2, dissimilarity='euclidean')
    # mda_result = sklearn_mda.fit_transform(people_ballots_sorted_list)
    #
    # fig2, ax2 = plt.subplots()
    # ax2.scatter(mda_result[0:90, 0], mda_result[0:90, 1])
    # for i, txt in enumerate(people_ids):
    #     ax2.annotate(str(txt), (mda_result[0:90, 0][i], mda_result[0:90, 1][i]))
    # plt.savefig('MDS.png')

    similarities = makeSimilarities(people_ballots_sorted_list)
    u, s, vT = np.linalg.svd(similarities)

    # fig3, ax3 = plt.subplots()
    # ax3.scatter(vT[1,:], vT[0,:])
    # for i, txt in enumerate(people_ids):
    #     ax3.annotate(str(txt), (vT[1,:][i], vT[0,:][i]))
    # plt.savefig('SVD.png')

    return createCompassDict(vT, people, people_ids)
