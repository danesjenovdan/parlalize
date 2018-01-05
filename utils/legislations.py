from parlaseje.models import Legislation, Vote
from parlalize.settings import LEGISLATION_STATUS, LEGISLATION_RESULT

# imported from settings
# LEGISLATION_STATUS = [('v obravnavi', 'v obravnavi'), ('konec obravnave', 'konec obravnave')]
# LEGISLATION_RESULT = [(None, 'Prazno'), ('sprejet', 'sprejet'), ('zavrnjen', 'zavrnjen')]

IN_PROCESS = LEGISLATION_STATUS[0][0]
FINISHED = LEGISLATION_STATUS[1][0]

ACCEPTED = LEGISLATION_RESULT[1][0]
REJECTED = LEGISLATION_RESULT[2][0]


def check_for_legislation_final_vote():
    legislations = Legislation.objects.filter(status=IN_PROCESS)
    for legislation in legislations:
        if legislation.epa:
            final_vote = Vote.objects.filter(epa=legislation.epa,
                                             motion__icontains='v celoti')
            repeated_vote = Vote.objects.filter(epa=legislation.epa,
                                                motion__icontains='ponovno odlo')
            mdt_vote = Vote.objects.filter(epa=legislation.epa,
                                           motion__icontains='sklep mdt')
            beginning_vote = Vote.objects.filter(epa=legislation.epa,
                                                 motion__icontains='sklep o primernosti predloga zakona')
            if final_vote:
                legislation.status = FINISHED
                if final_vote[0].result:
                    ## ACCEPTED
                    legislation.result = ACCEPTED
                else:
                    ## REJECTED
                    legislation.result = REJECTED
                legislation.save()

            if mdt_vote:
                if mdt_vote[0].result:
                    ## REJECTED
                    legislation.result = REJECTED
                    legislation.status = FINISHED
                    legislation.save()
                else:
                    ## FURTHER VOTING WILL HAPPEN
                    pass


            if beginning_vote:
                if not beginning_vote[0].result:
                    ## REJECTED
                    legislation.result = REJECTED
                    legislation.status = FINISHED
                    legislation.save()
                else:
                    ## FURTHER VOTING WILL HAPPEN
                    pass


def test_legislation_statuses():
    legislations = Legislation.objects.filter(status=FINISHED)
    for legislation in legislations:
        if legislation.epa:
            final_vote = Vote.objects.filter(epa=legislation.epa,
                                             motion__icontains='v celoti')
            repeated_vote = Vote.objects.filter(epa=legislation.epa,
                                                motion__icontains='ponovno odlo')
            mdt_vote = Vote.objects.filter(epa=legislation.epa,
                                           motion__icontains='sklep mdt')
            beginning_vote = Vote.objects.filter(epa=legislation.epa,
                                                 motion__icontains='sklep o primernosti predloga zakona')

            if final_vote:
                if repeated_vote:
                    if repeated_vote[0].result:
                        if legislation.result == ACCEPTED:
                        ## it's ok
                            pass
                        else:
                            print 'fail, had repeated vote, should be ACCEPTED', legislation.epa
                    else:
                        if legislation.result == REJECTED:
                            pass
                        else:
                            print 'fail, had repeated vote, should be REJECTED', legislation.epa
                else:
                    if final_vote[0].result:
                        if legislation.result == ACCEPTED:
                            ## it's ok
                            pass
                        else:
                            print 'fail', legislation.epa
            elif mdt_vote:
                if mdt_vote[0].result:
                    if legislation.result == REJECTED:
                        if legislation.status ==  FINISHED:
                            pass
                        else:
                            print 'je rejected ni pa finished', legislation.epa
                    else:
                        print 'mogu bi bit rejected', legislation.epa
            elif beginning_vote:
                if not beginning_vote[0].result:
                    if legislation.result == REJECTED:
                        if legislation.status ==  FINISHED:
                            pass
                        else:
                            print 'je rejected ni pa finished', legislation.epa
                    else:
                        print 'mogu bi bit rejected', legislation.epa
