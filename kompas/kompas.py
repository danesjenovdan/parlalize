from parlalize.models import Person, Ballot, Vote, Session
import ast, operator

def readResults():
    with open('results.dict', 'r') as f:
        s = f.read()
        return ast.literal_eval(s)

def getMPs():
    mps = requests.get('http://localhost:8000/api/getMPs/').json()

    mp_parladata_ids = [mp['id'] for mp in mps]

    people = Person.objects.filter(parladata_id__in=mp_parladata_ids)

    return people


def makeDictionary():
    votes = Vote.objects.all()
    persons = getMPs()

    results = {}

    for p1 in persons:
        print p1.name
        results[p1.id] = {}

        for p2 in persons:
            print 'Primerjam ' + p1.name + ' z: ' + p2.name

            this_person = 0

            for vote in votes:
                b1list = p1.ballot_set.filter(vote=vote)
                b2list = p2.ballot_set.filter(vote=vote)

                # first person has a ballot for this vote
                if len(b1list) > 0:
                    # first and second person have ballots
                    if len(b2list) > 0:
                        if b1list[0].option == b2list[0].option:
                            this_person = this_person + 1
                    # first person has a ballot, second doesn't
                    else:
                        if b1list[0].option == 'ni' or b1list[0].option == 'kvorum':
                            this_person = this_person + 1

                # first person doesn't have a ballot for this vote
                else:
                    # first has, second doesn't
                    if len(b2list) > 0:
                        if b2list[0].option == 'ni' or b2list[0].option == 'kvorum':
                            this_person = this_person + 1
                    # none have ballot
                    else:
                        this_person = this_person + 1
            results[p1.id][p2.id] = this_person

            print 'Rezultat je: ' + str(this_person)

    return results

def processResultsDictionary(results):
    a = []
    for i, p1 in enumerate(results):
        a.append([])
        for p2 in results[p1]:
            a[i].append(p2)

    return a

def calculateIdeology(P, results):
    u, s, vT = np.linalg.svd(P)
    ideology = vT[1, :]

    ideology_mapped = {}

    for i, p in enumerate(results):
        ideology_mapped[p] = ideology[i]

    sorted_results = sorted(ideology_mapped.items(), key=operator.itemgetter(1))

    # prints ideology paired
    for p in sorted_results:
        print Person.objects.get(id_parladata=p[0]).name + ' ' + str(p[1])

def calculateLeadership(P, nreps, results):
    # For each column, normalize so the sum is one. We started with an
	# identity matrix so even MoCs that only cosponsor their own bills
	# have some data. But if they have so little data, we should fudge
	# it because if they only 'cosponsor' their own bills they will get
	# leadership scores of 0.5.
	for col in xrange(nreps):
        s = sum(P[:,col])
        if s == 0: raise ValueError()

        if s < 10: # min number of cosponsorship data per person
            P[:,col] += (10.0-s)/nreps
			s = 10

        P[:,col] = P[:,col] / s

    # Create a random transition vector.
	v = numpy.ones( (nreps, 1) ) / float(nreps)

    # This is one minus the weight we give to the random transition probability
	# added into each column.
	c = 0.85

    # Create an initial choice for x, another random transition vector.
	x = numpy.ones( (nreps, 1) ) / float(nreps)

    # Run the Power Method to compute the principal eigenvector for the matrix,
	# which is, after all, the PageRank.

	while True:
		# Compute y = Ax where A is P plus some perturbation with magnitude
		# 1-c that ensures that A is a valid aperiodic, irreducible Markov transition matrix.
		y = c * numpy.dot(P, x)
		w = onenorm(x) - onenorm(y)
		y = y + w*v

		# Check the error and terminate if we are within tolerance.
		err = onenorm(y-x)
		if err < .00000000001:
			break

		x = y

	# Scale the values from 0 to 1 on a logarithmic scale.
	x = rescale(x, log=True)

	return x # this is the pagerank
