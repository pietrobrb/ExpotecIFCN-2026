from typing import Any
from django import forms
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from atividades.models import Sala, TipoAtividade
from chamadas.filtersets import TipoChamadaFilter
from chamadas.models import TipoChamada
from core.mixins import ActionTabsViewMixin
from core.views import CreateView, CreateWithInlinesView, DeleteView, DetailView, EditView, EditWithInlinesView, FormView, TableListView
from core.viewsets import ViewSet
from eventos.filtersets import (
    AreaTematicaFilter,
    AvaliadorFilter, 
    ComissaoFilter, 
    EventoDocumentoFilter,
    ItemGaleriaFilter,
    NoticiaFilter, 
    ParceiroFilter, 
    
)
from atividades.filtersets import (
    SalaFilter,
    TipoAtividadeFilter
)
from eventos.forms import (
    EventoAreaTematicaForm, 
    EventoComissaoForm,
    EventoContatoInline, 
    EventoDocumentoForm,
    EventoEnderecoMultiForm,
    EventoItemGaleriaForm, 
    EventoMembroComissaoForm,
    EventoMembroComissaoInline,
    EventoNoticiaForm,
    EventoParceiroForm, 
)
from eventos.models import AreaTematica, Comissao, Evento, EventoDocumento, ItemGaleria, Noticia, Parceiro, Avaliador
from eventos.tables import (
    EventoAreaTematicaTable,
    EventoAvaliadoresTable, 
    EventoComissaoTable, 
    EventoDocumentoTable,
    EventoItemGaleriaTable,
    EventoParceiroTable,
    EventoSalaTable, 
    EventoTipoAtividadeTable,
    EventoTipoChamadaTable
)
from usuarios.models import User

eventos_vs = ViewSet(Evento)

areas_tematicas_vs = ViewSet(AreaTematica)
documentos_vs = ViewSet(EventoDocumento)
comissoes_vs = ViewSet(Comissao)
parceiros_vs = ViewSet(Parceiro)
noticias_vs = ViewSet(Noticia)
avaliador_vs = ViewSet(Avaliador)
itemgaleria_vs = ViewSet(ItemGaleria)

@eventos_vs.action(
    "detalhar",
    verbose_name="Apresentação",
    hidden=True,
    tab=True
)
class EventoDetailView(ActionTabsViewMixin, DetailView):
    model = Evento
    permission_required = ["is_admin_rule", "is_member_rule"]
    template_name = "evento_detail.html"
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']

    def get_parent(self):
        return self.request.evento

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.evento
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evento = self.get_object()
        form = EventoEnderecoMultiForm(instance=evento)
         
        inline_instance = EventoContatoInline(Evento, request=self.request, instance=evento)
        contato_forms = inline_instance.construct_formset()
        form['evento'].fields['logo'].widget = forms.TextInput()
        form['evento'].fields['logo_mini'].widget = forms.TextInput()
        form['evento'].fields['imagem_promocional'].widget = forms.TextInput()
        form['evento'].fields['video_promocional'].widget = forms.TextInput()
        form['evento'].fields['apresentacao'].widget = forms.Textarea()
        # Desabilita todos os campos para visualização apenas (não editável)
        for form_key in form.forms:
            for field_name, field in form.forms[form_key].fields.items():
                field.widget.attrs['disabled'] = 'disabled'

        # Desabilita todos os campos no formset dos inlines
        for cf in contato_forms:
            for field_name, field in cf.fields.items():
                field.widget.attrs['disabled'] = 'disabled'

        context['form'] = form
        context['contato_forms'] = contato_forms
        context['page_title'] = f"Evento"
      
        return context
    
@eventos_vs.action("edit")
class EventoEditView(EditWithInlinesView):
    model = Evento
    permission_required = ["is_admin_rule", "is_member_rule"]
    form_class = EventoEnderecoMultiForm
    inlines = [EventoContatoInline]
    inlines_names = ["contato_forms"]
    template_name = "evento_form.html"
    
    def get_success_url(self) -> str:
        return reverse("evento:evento-detalhar") 
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        form = self.get_form(self.get_form_class())
        inlines = self.construct_inlines()


        # Verifica se o formulário principal e os inlines são válidos
        if form.is_valid() and all(inline_formset.is_valid() for inline_formset in inlines):
            return self.forms_valid(form, inlines)
        else:
            return self.forms_invalid(form, inlines)
        
    def forms_valid(self, form, inlines):
        # Salva o formulário principal (evento)
        evento = form['evento'].save(commit=False)
        
        # Salva o formulário de endereço, caso haja
        endereco = form['endereco'].save(commit=False)
        endereco.save()

        # Associa o endereço ao evento e salva o evento
        evento.endereco = endereco
        evento.save()

        # Salva os formulários inline (contatos)
        for inline_formset in inlines:
            # Itera sobre cada formulário individual no formset
            for f in inline_formset:
                if f.is_valid():
                    inline_instance = f.save(commit=False)
                    inline_instance.evento = evento  # Associa o evento à instância
                    inline_instance.save()

        # Finalmente, chama o método padrão do Django para redirecionar ou processar a resposta
        return super().forms_valid(form, inlines)



#@tipo_atividades_vs.action('list')
@eventos_vs.action(
    "tipoatividades",
    verbose_name="Tipos de Atividade",
    hidden=True,
    tab=True,
    icon='fas fa-star',
    add_url="atividade:tipoatividade-add"
)
class EventoTipoAtividadeListView(ActionTabsViewMixin, TableListView):
    model = TipoAtividade
    filterset_class = TipoAtividadeFilter
    paginate_by = 10  
    permission_required = ["is_admin_rule", "is_member_rule"]
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']
    template_name = "list_detail.html"
    table_class = EventoTipoAtividadeTable

    def get_parent(self):
        return self.request.evento
    
    def get_queryset(self):
        return TipoAtividade.objects.filter(evento = self.get_parent())
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['page_title'] = f"Evento"
        return context
    


#@areas_tematicas_vs.action('list')
@eventos_vs.action(
    "areas_tematicas",
    verbose_name="Áreas",
    hidden=True,
    tab=True,
    icon='fas fa-clone',
    add_url = "evento:areatematica-add"
)
class EventoAreaTematicaListView(ActionTabsViewMixin, TableListView):
    model = AreaTematica
    filterset_class = AreaTematicaFilter
    paginate_by = 10  
    permission_required = ["is_admin_rule", "is_member_rule"]
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']
    template_name = "list_detail.html"
    table_class = EventoAreaTematicaTable
    
    def get_parent(self):
        return self.request.evento
    
    def get_queryset(self):
        return AreaTematica.objects.filter(evento = self.get_parent())
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['page_title'] = f"Evento"
        return context

@areas_tematicas_vs.action('add')
class EventoAreaTematicaCreateView(CreateView):
    model = AreaTematica
    form_class = EventoAreaTematicaForm
    permission_required = ["is_admin_rule"]
    def get_success_url(self) -> str:
        return reverse("evento:evento-areas_tematicas")
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@areas_tematicas_vs.action('edit')
class EventoAreaTematicaEditView(EditView):
    model = AreaTematica
    form_class = EventoAreaTematicaForm
    permission_required = ["is_admin_rule", "is_member_rule"]
    def get_success_url(self) -> str:
        return reverse("evento:evento-areas_tematicas")
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@areas_tematicas_vs.action('detail')
class EventoAreaTematicaDetailView(DetailView):
    model = AreaTematica
    detail_fields = ['nome', 'descricao', 'cor', 'icone']
    permission_required = ["is_admin_rule", "is_member_rule"]

@areas_tematicas_vs.action('delete', modal=True)
class EventoAreaTematicaDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-areas_tematicas")
@eventos_vs.action(
    "eventodocumento",
    verbose_name="Documentos",
    hidden=True,
    tab=True,
    icon='fas fa-copy',
    add_url="evento:eventodocumento-add"
)
class EventoDocumentoListView(ActionTabsViewMixin, TableListView):
    model = EventoDocumento
    filterset_class = EventoDocumentoFilter
    paginate_by = 10  # Número de itens por página
    permission_required = ["is_admin_rule", "is_member_rule"]
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']
    template_name = "list_detail.html"
    table_class = EventoDocumentoTable

    def get_parent(self):
        return self.request.evento
    
    def get_queryset(self):
        return EventoDocumento.objects.select_related('evento', 'documento').filter(evento = self.get_parent())
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['page_title'] = f"Evento"
        return context
    
@documentos_vs.action('add')
class EventoDocumentoCreateView(CreateView):
    model = EventoDocumento
    form_class = EventoDocumentoForm
    permission_required = ["is_admin_rule"]
    def get_success_url(self) -> str:
        return reverse("evento:evento-eventodocumento")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)
    
@documentos_vs.action('view', icon='fas fa-eye', verbose_name='Visualizar',item=True , target='_blank')
class EventoDocumentoDetailView(DetailView):
    model = EventoDocumento
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get(self, request, *args, **kwargs):
        evento_documento = self.get_object()
        return HttpResponseRedirect(evento_documento.documento.file.url)
        
@documentos_vs.action('edit')
class EventoDocumentoEditView(EditView):
    model = EventoDocumento
    form_class = EventoDocumentoForm
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-eventodocumento")
   

@documentos_vs.action('delete',  modal=True)
class EventoDocumentoDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]
    def get_success_url(self) -> str:
        return reverse("evento:evento-eventodocumento")
   

@eventos_vs.action(
    "comissoes",
    verbose_name="Comissões",
    hidden=True,
    tab=True,
    icon='fas fa-people-group',
    add_url = "evento:comissao-add"
)
class EventoComissaoListView(ActionTabsViewMixin,TableListView):
    model = Comissao
    filterset_class = ComissaoFilter
    permission_required = ["is_admin_rule", "is_member_rule"]
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']
    template_name = "list_detail.html"
    table_class = EventoComissaoTable

    def get_parent(self):
        return self.request.evento
    
    def get_queryset(self):
        return Comissao.objects.filter(evento = self.get_parent())
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['page_title'] = f"Evento"
        return context

@comissoes_vs.action('add')
class EventoComissaoCreateView(CreateWithInlinesView):
    model = Comissao
    form_class = EventoComissaoForm
    inlines = [EventoMembroComissaoInline]
    inlines_names = ["membro_forms"]
    template_name = "evento_comissao_form.html"
    permission_required = ["is_admin_rule"]
    
    def get_success_url(self) -> str:
        return reverse("evento:evento-comissoes")
    
    def forms_valid(self, form, inlines):
        # Salva o formulário principal (comissao)
        comissao = form.save(commit=False)
        comissao.evento = self.request.evento
        comissao.save()

        # Salva os formulários inline (membros)
        for inline_formset in inlines:
            # Itera sobre cada formulário individual no formset
            for f in inline_formset:
                if f.is_valid():
                    # Verifica se já existe um usuário com o email fornecido
                    email = f.cleaned_data['email']
                    user, created = User.objects.update_or_create(
                        email=email,
                        defaults={
                            'nome_completo': f.cleaned_data['nome_completo'],
                            'vinculo': f.cleaned_data['vinculo'],
                        }
                    )
                    
                    inline_instance = f.save(commit=False)
                    inline_instance.usuario = user
                    inline_instance.comissao = comissao
                    inline_instance.save()
                        

        # Finalmente, chama o método padrão do Django para redirecionar ou processar a resposta
        return super().forms_valid(form, inlines)

@comissoes_vs.action('edit')
class EventoComissaoEditView(EditWithInlinesView):
    model = Comissao
    form_class = EventoComissaoForm
    inlines = [EventoMembroComissaoInline]
    inlines_names = ["membro_forms"]
    template_name = "evento_comissao_form.html"
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-comissoes")
    
    def get_object(self, queryset=None):
        self.object = get_object_or_404(Comissao, pk=self.kwargs.get("pk"))
        return self.object
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def forms_valid(self, form, inlines):
        # Salva o formulário principal (comissao)
        comissao = form.save(commit=False)
        comissao.evento = self.request.evento
        comissao.save()

        # Salva os formulários inline (membros)
        for inline_formset in inlines:
            # Itera sobre cada formulário individual no formset
            for f in inline_formset:
                if f.is_valid():
                    # Verifica se já existe um usuário com o CPF fornecido
                    email = f.cleaned_data['email']
                    user_data = {
                        'nome_completo': f.cleaned_data['nome_completo'],
                        'vinculo': f.cleaned_data['vinculo'],
                    }
                  
                    user, created = User.objects.update_or_create(
                        email=email,
                        defaults=user_data
                    )
                        
                    inline_instance = f.save(commit=False)
                    inline_instance.usuario = user
                    inline_instance.comissao = comissao
                    inline_instance.save()
                        

        # Finalmente, chama o método padrão do Django para redirecionar ou processar a resposta
        return super().forms_valid(form, inlines)

@comissoes_vs.action('detail')
class EventoComissaoDetailView(DetailView):
    model = Comissao
    detail_fields = ['nome']
    permission_required = ["is_admin_rule", "is_member_rule"]
    

@comissoes_vs.action('delete')
class EventoComissaoDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-comissoes")

#@parceiros_vs.action('list')
@eventos_vs.action(
    "parceiros",
    verbose_name="Parceiros",
    hidden=True,
    tab=True,
    icon='fas fa-handshake',
    add_url="evento:parceiro-add"
)
class EventoParceiroListView(ActionTabsViewMixin, TableListView):
    model = Parceiro
    filterset_class = ParceiroFilter
    paginate_by = 10  
    permission_required = ["is_admin_rule", "is_member_rule"]
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']
    template_name = "list_detail.html"
    table_class = EventoParceiroTable
    def get_parent(self):
        return self.request.evento
    
    def get_queryset(self):
        return Parceiro.objects.filter(evento = self.get_parent())
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['page_title'] = f"Evento"
        return context
    
@eventos_vs.action(
    "itensgaleria",
    verbose_name="Item Galeria",
    hidden=True,
    tab=True,
    icon='fas fa-handshake',
    add_url="evento:itemgaleria-add"
)
class EventoItemGaleriaListView(ActionTabsViewMixin, TableListView):
    model = ItemGaleria
    filterset_class = ItemGaleriaFilter
    paginate_by = 10  
    permission_required = ["is_admin_rule", "is_member_rule"]
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']
    template_name = "list_detail.html"
    table_class = EventoItemGaleriaTable
    def get_parent(self):
        return self.request.evento
    
    def get_queryset(self):
        return ItemGaleria.objects.filter(evento = self.get_parent())
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['page_title'] = f"Evento"
        return context
    
@parceiros_vs.action('add')
class EventoParceiroCreateView(CreateView):
    model = Parceiro
    form_class = EventoParceiroForm
    permission_required = ["is_admin_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-itensgaleria")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@itemgaleria_vs.action('add')
class EventoItemGaleriaCreateView(CreateView):
    model = ItemGaleria
    form_class = EventoItemGaleriaForm
    permission_required = ["is_admin_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-itensgaleria")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@parceiros_vs.action('edit')
class EventoParceiroEditView(EditView):
    model = Parceiro
    form_class = EventoParceiroForm
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-parceiros")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@itemgaleria_vs.action('edit')
class EventoItemGaleriaEditView(EditView):
    model = ItemGaleria
    form_class = EventoItemGaleriaForm
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-itensgaleria")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@parceiros_vs.action('detail')
class EventoParceiroDetailView(DetailView):
    model = Parceiro
    detail_fields = ['nome', 'url', 'logo']
    permission_required = ["is_admin_rule", "is_member_rule"]

@itemgaleria_vs.action('detail')
class EventoItemGaleriaDetailView(DetailView):
    model = ItemGaleria
    detail_fields = ['titulo', 'url', 'img']
    permission_required = ["is_admin_rule", "is_member_rule"]


@parceiros_vs.action('delete', modal=True)
class EventoParceiroDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-parceiros")

@itemgaleria_vs.action('delete', modal=True)
class EventoItemGaleriaDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:evento-itensgaleria")
    

@noticias_vs.action('list')
class EventoNoticiasListView(TableListView):
    model = Noticia
    filterset_class = NoticiaFilter
    permission_required = ["is_admin_rule", "is_member_rule"]
    list_display = ["id","titulo", "subtitulo", "ordem"]
    
    def get_queryset(self):
        return Noticia.objects.filter(evento = self.request.evento)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['page_title'] = f"Evento"
        return context

@noticias_vs.action('add')
class EventoNoticiaCreateView(CreateView):
    model = Noticia
    form_class = EventoNoticiaForm
    permission_required = ["is_admin_rule"]
    
    def get_success_url(self) -> str:
        return reverse("evento:noticia-list")
    
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@noticias_vs.action('edit')
class EventoNoticiaEditView(EditView):
    model = Noticia
    form_class = EventoNoticiaForm
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:noticia-list")
    def form_valid(self, form):
        form.instance.evento = self.request.evento
        return super().form_valid(form)

@noticias_vs.action('detail')
class EventoNoticiaDetailView(DetailView):
    template_name = "evento_noticia_detail.html"
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:noticia-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = EventoNoticiaForm(instance=self.get_object())
        form.fields['poster'].widget = forms.TextInput()
        form.fields['thumbnail'].widget = forms.TextInput()
        for field in form.fields.values():
            field.widget.attrs['disabled'] = 'disabled'
        
        
        context['form'] = form
        return context


@noticias_vs.action('delete', modal=True)
class EventoNoticiaDeleteView(DeleteView):
    permission_required = ["is_admin_rule"]

    def get_success_url(self) -> str:
        return reverse("evento:noticia-list")
    
@eventos_vs.action("get_user", item=False, hidden=True)
class UserMemberForm(FormView):
    form_class = EventoMembroComissaoForm
    permission_required = ["is_admin_rule", "is_member_rule"]

    def get(self, request, *args, **kwargs):
        email = request.GET.get("email")
        user = User.objects.filter(email=email).first()
        if user is not None:
            user_data = {
                "id": user.id,
                "nome_completo": user.nome_completo,
                "email": user.email,
                "cpf": user.cpf,
                "vinculo": user.vinculo,
                "foto_perfil": user.foto_perfil.url if user.foto_perfil else None,
            }
            return JsonResponse({"found":True, "usuario": user_data})
        else:
            user_data = {
                "email": email
            }
            return JsonResponse({"found":False, "usuario": user_data})


@eventos_vs.action(
    "tipochamadas",
    verbose_name="Tipos de Chamadas",
    hidden=True,
    tab=True,
    icon='fas fa-graduation-cap',
    add_url="chamada:tipochamada-add"
)
class EventoTipoChamadaListView(ActionTabsViewMixin, TableListView):
    model = TipoChamada
    filterset_class = TipoChamadaFilter
    permission_required = ["is_admin_rule", "is_member_rule"]
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']
    template_name = "list_detail.html"
    table_class = EventoTipoChamadaTable

    def get_parent(self):
        return self.request.evento
    
    def get_queryset(self):
        return TipoChamada.objects.filter(evento = self.request.evento)

@eventos_vs.action(
    "salas",
    verbose_name="Salas",
    hidden=True,
    tab=True,
    icon='fas fas fa-door-closed',
    add_url="atividade:sala-add"
)
class EventoSalasListView(ActionTabsViewMixin, TableListView):
    model = Sala
    filterset_class = SalaFilter
    permission_required = ["is_admin_rule", "is_member_rule"]
    parent_details = ['titulo', 'subtitulo', 'edicao', 'ano', 'dt_inicio', 'dt_encerramento']
    template_name = "list_detail.html"
    table_class = EventoSalaTable

    def get_parent(self):
        return self.request.evento
    
    def get_queryset(self):
        return Sala.objects.filter(evento = self.request.evento)

@avaliador_vs.action(
    "list",
    verbose_name="Avaliadores Inscritos",
    icon='fas fa-graduation-cap'
)
class EventoAvaliadoresListView(TableListView):
    model = Avaliador
    filterset_class = AvaliadorFilter
    permission_required = ["is_admin_rule", "is_member_rule"]
    template_name = "evento_avaliadores.html"
    table_class = EventoAvaliadoresTable
    
    def get_queryset(self):
        return Avaliador.objects.filter(evento = self.request.evento)
