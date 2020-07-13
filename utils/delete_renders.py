from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from parlaposlanci.models import Tfidf as pTfidf, MPStaticPL
from parlaskupine.models import Tfidf as pgTfidf, PGStatic
from parlaseje.models import Tfidf as sTfidf, Vote
from parlalize.utils_ import getAllStaticData

import requests

methods = {
    MPStaticPL: {'group': 'p', 'method': 'osnovne-informacije', 'app': 'person'},
    pTfidf: {'group': 'p', 'method': 'tfidf', 'app': 'person'},
    pgTfidf: {'group': 'ps', 'method': 'tfidf', 'app': 'organization'},
    sTfidf: {'group': 's', 'method': 'tfidf', 'app': 'session'},
    PGStatic : {'group': 'ps', 'method': 'osnovne-informacije', 'app': 'organization'},
}


def delete_renders(method=None, group=None, owner_id=None, renders=None):
    if settings.GLEJ_URL:
        url = settings.GLEJ_URL+'/api/cards/renders/delete/all'

        attrs = []

        if method:
            attrs.append('method='+method)
        if group:
            attrs.append('group='+group)
        if owner_id:
            attrs.append('id='+str(owner_id))
        if attrs:
            url = url + '?' + '&'.join(attrs)
        requests.get(url)



@receiver(post_save, sender=pTfidf)
@receiver(post_save, sender=pgTfidf)
@receiver(post_save, sender=sTfidf)
def deleteRendersOfTfidfs(sender, instance, **kwargs):
    if instance.is_visible:
        deleteRendersOfCard(sender, instance)


@receiver(post_save, sender=MPStaticPL)
@receiver(post_save, sender=PGStatic)
def deleteRendersOfCard(sender, instance, **kwargs):
    attrs = methods[sender]
    owner_id = getattr(instance, methods[sender]['app']).id_parladata
    delete_renders(method=attrs['method'], group=attrs['group'], owner_id=owner_id)


def deleteRendersOfSession(session_ids, update_votes_details=False, update_speeches=False):
    # delete renders votes of session
    for session_id in session_ids:
        delete_renders(group='s', method='seznam-glasovanj', owner_id=str(session_id))

        # delete renders vote details
        if update_votes_details:
            votes = Vote.objects.filter(session_id__id_parladata=session_id)
            if votes:
                # delete legislations
                delete_renders(group='c', method='zakonodaja', owner_id=str(session_id))
            for vote in votes:
                delete_renders(group='s', method='glasovanje', owner_id=str(vote.id_parladata))

        # delete last session
        delete_renders(group='c', method='zadnja-seja')

        if update_speeches:
            delete_renders(group='s', method='govori', owner_id=str(session_id))



# TODO
# settings.HAS_LEGISLATIONS

def deleteRendersOfIDs(owner_ids, group, method):
    for owner_id in owner_ids:
        delete_renders(group=group, method=method, owner_id=owner_id)

def deleteMPandPGsRenders():
    delete_renders(group='p')
    delete_renders(group='ps')

def deleteSessionsRenders():
    delete_renders(group='s')


def refetch():
    getAllStaticData(None, force_render=True)
    requests.get(settings.GLEJ_URL+'/api/data/refetch')
    requests.get(settings.FRONT_URL+'/api/data/refetch')
    requests.get(settings.ISCI_URL+'/api/data/refetch')
