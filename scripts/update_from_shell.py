from utils.runner import update, fastUpdate
from raven.contrib.django.raven_compat.models import client
from utils.solr_export import exportSpeeches


def run(*args):
    # skip recache lastactivity and speeches
    try:
        skipPersonRecache = True if 'fastUpdate' in args else False
        fastUpdate(fast=skipPersonRecache)
        exportSpeeches()
    except:
        client.captureException()
