from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person, MinisterStatic
from parlaskupine.models import Organization
from parlaseje.models import Session, Question
from parlalize.settings import API_URL
from utils.parladata_api import getQuestions


class Command(BaseCommand):
    help = 'Updates people from Parladata'

    def handle(self, *args, **options):
        data = getQuestions()
        existingISs = list(Question.objects.all().values_list("id_parladata",
                                                          flat=True))
        for dic in data:
            if int(dic["id"]) not in existingISs:
                if dic['session']:
                    session = Session.objects.get(id_parladata=int(dic['session']))
                else:
                    session = None
                links = getLinks(question=dic['id'])
                link = links[0]['url'] if links else None
                person = []
                for i in dic['authors']:
                    person.append(Person.objects.get(id_parladata=int(i)))
                if dic['recipient_person']:
                    rec_p = list(Person.objects.filter(id_parladata__in=dic['recipient_id']))
                else:
                    rec_p = []
                if dic['recipient_organization']:
                    rec_org = list(Organization.objects.filter(id_parladata__in=dic['recipient_org_id']))
                else:
                    rec_org = []
                author_org = []
                for i in dic['author_orgs']:
                    author_org.append(Organization.objects.get(id_parladata=i))
                rec_posts = []
                for post in dic['recipient_post']:
                    static = MinisterStatic.objects.filter(person__id=post['membership__person_id'],
                                                        ministry=post['organization_id'])
                    if static:
                        rec_posts.append(static[0])
                question = Question(session=session,
                                    start_time=dic['date'],
                                    id_parladata=dic['id'],
                                    recipient_text=dic['recipient_text'],
                                    title=dic['title'],
                                    content_link=link,
                                    type_of_question=dic['type_of_question']
                                    )
                question.save()
                question.author_orgs.add(*author_org)
                question.person.add(*person)
                question.recipient_persons.add(*rec_p)
                question.recipient_organizations.add(*rec_org)
                question.recipient_persons_static.all(*rec_posts)
            else:
                print "update question"
                person = []
                for i in dic['author_id']:
                    person.append(Person.objects.get(id_parladata=int(i)))
                if dic['recipient_id']:
                    rec_p = list(Person.objects.filter(id_parladata__in=dic['recipient_id']))
                else:
                    rec_p = []
                if dic['recipient_org_id']:
                    rec_org = list(Organization.objects.filter(id_parladata__in=dic['recipient_org_id']))
                else:
                    rec_org = []
                author_org = []
                for i in dic['author_org_id']:
                    author_org.append(Organization.objects.get(id_parladata=i))
                rec_posts = []
                for post in dic['recipient_posts']:
                    static = MinisterStatic.objects.filter(person__id_parladata=post['membership__person_id'],
                                                        ministry__id_parladata=post['organization_id']).order_by('-created_for')
                    if static:
                        rec_posts.append(static[0])
                question = Question.objects.get(id_parladata=dic["id"])
                question.save()
                question.author_orgs.add(*author_org)
                question.person.add(*person)
                question.recipient_persons.add(*rec_p)
                question.recipient_organizations.add(*rec_org)
                question.recipient_persons_static.add(*rec_posts)
        return 0