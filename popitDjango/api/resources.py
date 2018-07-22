from tastypie.resources import ModelResource
from api.models import Note, article
from tastypie.authorization import Authorization

class NoteResource(ModelResource):
    class Meta:
        queryset = Note.objects.all()
        resource_name = 'note'
        authorization = Authorization()

class articleResource(ModelResource):
    class Meta:
        queryset = article.objects.all()
        resource_name = 'article'
        authorization = Authorization()