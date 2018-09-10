from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from parlaposlanci.models import Tfidf as pTfidf, MPStaticPL
from parlaskupine.models import Tfidf as pgTfidf, PGStatic
from parlaseje.models import Tfidf as sTfidf, Vote

import requests

methods = {
    MPStaticPL: {'group': 'p', 'method': 'osnovne-informacije', 'app': 'person'},
    pTfidf: {'group': 'p', 'method': 'tfidf', 'app': 'person'},
    pgTfidf: {'group': 'ps', 'method': 'tfidf', 'app': 'organization'},
    sTfidf: {'group': 's', 'method': 'tfidf', 'app': 'session'},
    PGStatic : {'group': 'ps', 'method': 'osnovne-informacije', 'app': 'organization'},
}


def delete_renders(method=None, group='p', owner_id=None, renders=None):
    if settings.GLEJ_URL:
        def match(item):
            if owner_id:
                if str(item['id']) != str(owner_id):
                    return False
            if group != item['group']:
                return False
            if method:
                if method != item['method']:
                    return False
            return True

        if not renders:
            url = settings.GLEJ_URL + '/api/cards/renders'
            renders = requests.get(url).json()

        cards = [render['_id'] for render in filter(lambda x: match(x), renders['docs'])]
        for card_id in cards:
            url = settings.GLEJ_URL + '/api/cards/renders/delete/' + card_id
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


def deleteRendersOfSessionVotes(session_id):
    votes = Vote.objects.filter(session_id__id_parladata=session_id)

    # delete renders votes of session
    delete_renders(method='seznam-glasovanj', group='s', owner_id=session_id)

    # delete renders vote details
    url = settings.GLEJ_URL + '/api/cards/renders'
    renders = requests.get(url).json()

    for vote in votes:
        delete_renders(method='glasovanje', group='s', owner_id=vote.id_parladata, renders=renders)

    # delete last session
    delete_renders(method='zadnja-seja', group='c', owner_id=None)


# TODO
# settings.HAS_LEGISLATIONS

def deleteMPandPGsRenders():
    delete_renders(group='p')
    delete_renders(group='ps')

