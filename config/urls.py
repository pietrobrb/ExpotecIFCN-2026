from django.contrib import admin
from django.urls import path
from django.urls import  include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core.views import EmBreveView
from django_summernote.views import SummernoteUploadAttachment

urlpatterns = [
    path("", RedirectView.as_view(url="portal/"), name='home'),
    path('portal/', include('portal.urls')),
    path('users/', include('usuarios.urls')),
    path('eventos/', include('eventos.urls')),
    path('atividades/', include('atividades.urls')),
    path('chamadas/', include('chamadas.urls')),
    path("select2/", include("django_select2.urls")),
    path('accounts/', include('allauth.urls')),
    path('submissao/', include('submissao.urls')),
    path('credenciamento/', include('credenciamento.urls')),
    path("embreve", EmBreveView.as_view(), name='embreve'),
    path('summernote/', include('django_summernote.urls')),
    path('summernote/upload_attachment/', SummernoteUploadAttachment.as_view(), name='django_summernote-upload_attachment'),
    path('admin/', admin.site.urls),
]



urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
