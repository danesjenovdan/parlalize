from parlaseje.models import Legislation, Vote
from parlalize.settings import LEGISLATION_STATUS, LEGISLATION_RESULT
from parlalize.utils_ import lockSetter

from django.http import JsonResponse

# imported from settings
# LEGISLATION_STATUS = [('v obravnavi', 'v obravnavi'), ('konec obravnave', 'konec obravnave')]
# LEGISLATION_RESULT = [(None, 'Prazno'), ('sprejet', 'sprejet'), ('zavrnjen', 'zavrnjen')]

IN_PROCESS = LEGISLATION_STATUS[0][0]
FINISHED = LEGISLATION_STATUS[1][0]

ACCEPTED = LEGISLATION_RESULT[0][0]
REJECTED = LEGISLATION_RESULT[2][0]


@lockSetter
def check_for_legislation_final_vote(request):
    legislations = Legislation.objects.filter(status=IN_PROCESS)
    stats = {'finished': 0,
             'mdt': 0,
             'beginning': 0}
    for legislation in legislations:
        resp = set_legislation_result(legislation)
        if resp:
            stats[resp] += 1
    return JsonResponse({'status': 'done',
                         'report': 'finished: ' + str(stats['finished']) + ', mdt: ' + str(stats['mdt']) + ', beginning: ' + str(stats['beginning'])},
                        safe=False) 

def finish_legislation_by_final_vote(vote):
    if any(word in vote.motion for word in ['v celoti',
                                            'ponovno odlo',
                                            'sklep mdt',
                                            'sklep o primernosti predloga zakona']):
        if vote.epa:
            legislation = Legislation.objects.filter(epa=vote.epa)
            if legislation:
                set_legislation_result(legislation[0])


def set_legislation_result(legislation):
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
                if is_accepeted(final_vote[0]):
                    ## ACCEPTED
                    legislation.result = ACCEPTED
                else:
                    ## REJECTED
                    legislation.result = REJECTED
                legislation.save()
                return 'finished'

            elif mdt_vote:
                if is_accepeted(mdt_vote[0]):
                    ## REJECTED
                    legislation.result = REJECTED
                    legislation.status = FINISHED
                    legislation.save()
                    return 'mdt'
                else:
                    ## FURTHER VOTING WILL HAPPEN
                    pass


            elif beginning_vote:
                if not is_accepeted(beginning_vote[0]):
                    ## REJECTED
                    legislation.result = REJECTED
                    legislation.status = FINISHED
                    legislation.save()
                    return 'beginning'
                else:
                    ## FURTHER VOTING WILL HAPPEN
                    pass
    return None


@lockSetter
def test_legislation_statuses(request):
    legislations = Legislation.objects.filter(status=FINISHED)
    fails = []
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
                    if is_accepeted(repeated_vote[0]):
                        if legislation.result == ACCEPTED:
                        ## it's ok
                            pass
                        else:
                            fails.append({'desc': 'fail, had repeated vote, should be ACCEPTED',
                                          'epa': legislation.epa,
                                          'id': legislation.id})
                    else:
                        if legislation.result == REJECTED:
                            pass
                        else:
                            fails.append({'desc': 'fail, had repeated vote, should be REJECTED',
                                          'epa': legislation.epa,
                                          'id': legislation.id})
                else:
                    if is_accepeted(final_vote[0]):
                        if legislation.result == ACCEPTED:
                            ## it's ok
                            pass
                        else:
                            fails.append({'desc': 'fail final vote, should be ACCEPTED',
                                          'epa': legislation.epa,
                                          'id': legislation.id})
                    else:
                        if legislation.result == REJECTED:
                            ## it's ok
                            pass
                        else:
                            fails.append({'desc': 'fail final vote, should be REJECTED',
                                          'epa': legislation.epa,
                                          'id': legislation.id})
            elif mdt_vote:
                if is_accepeted(mdt_vote[0]):
                    if legislation.result == REJECTED:
                        if legislation.status ==  FINISHED:
                            pass
                        else:
                            fails.append({'desc': 'je rejected ni pa finished',
                                          'epa': legislation.epa,
                                          'id': legislation.id})
                    else:
                        fails.append({'desc': 'mogu bi bit rejected',
                                      'epa': legislation.epa,
                                      'id': legislation.id})
            elif beginning_vote:
                if not is_accepeted(beginning_vote[0]):
                    if legislation.result == REJECTED:
                        if legislation.status ==  FINISHED:
                            pass
                        else:
                            fails.append({'desc': 'je rejected ni pa finished',
                                          'epa': legislation.epa,
                                          'id': legislation.id})
                    else:
                        fails.append({'desc': 'mogu bi bit rejected',
                                      'epa': legislation.epa,
                                      'id': legislation.id})
    return JsonResponse(fails, safe=False)


# is legislation accepted
def is_accepeted(vote):
    accepted_option = False if 'ni primeren' in vote.motion else True
    return vote.result == accepted_option
