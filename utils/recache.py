from datetime import datetime, timedelta
# from raven.contrib.django.raven_compat.models import client

from parlaskupine.views import getListOfPGs, getIntraDisunionOrg
from parlaseje.views import getSessionsList
from parlaskupine.models import Organization
from django.conf import settings
from parlalize.utils_ import getAllStaticData
from django.db.models import Q
from slack import WebClient
slack_client = WebClient(token=settings.SLACK_TOKEN)

def updateCacheforList(date_=None):
    """
    Method which runs once per day (cron job)
    for recache cache with short lifetime
    """
    try:
        if not date_:
            tomorrow = datetime.now() + timedelta(days=1)
            date_ = tomorrow.strftime(settings.API_DATE_FORMAT)
        getAllStaticData(None, force_render=True)
        getListOfPGs(None, date_, force_render=True)
        getSessionsList(None, date_, force_render=True)
        updateCacheIntraDisunion()
        # store static data for search

        slack_client.chat_postMessage(
            channel='#parlalize_notif',
            text='Zgeneriru sem cache za nasledn dan.'
        )

    except:
        # client.captureException()
        slack_client.chat_postMessage(
                channel="#parlalize_notif",
                text='Upss neki je šlo narobe. Nisem zgeneriru cache-a.'
        )

    return 1


def updateCacheIntraDisunion():
    organizatons = Organization.objects.filter(Q(classification=settings.PS) |
                                               Q(classification='stran_vlade') |
                                               Q(name='Državni zbor')).values_list('id_parladata', flat=True)
    for org in organizatons:
        getIntraDisunionOrg(None, str(org), force_render=True)

    return 1
