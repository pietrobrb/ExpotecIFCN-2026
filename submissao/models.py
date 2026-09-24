from django.db import models
from core.models import get_hoje, validate_future_date
from documentos.models import Documento, TipoDocumento
from eventos.models  import AreaTematica
from chamadas.models import EtapaChamada, FormaAvaliacao, StatusChamada, TipoChamada, Chamada, CriterioAvaliacao
from usuarios.models import User
from eventos.models import Avaliador
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum
from django.utils.html import format_html
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
class StatusTrabalho(models.TextChoices):
    RASCUNHO = 'RASCUNHO', _('Rascunho')
    SUBMETIDO = 'SUBMETIDO', _('Submetido')
    EM_AVALIACAO = 'EM_AVALIACAO', _('Em Avaliação')
    APROVADO = 'APROVADO', _('Aprovado')
    REPROVADO = 'REPROVADO', _('Reprovado')
    APRESENTADO = 'APRESENTADO', _('Apresentado')
    N_APRESENTADO = 'N_APRESENTADO', _('Não Apresentado')
    

class Trabalho(models.Model):
    area_tematica = models.ForeignKey(AreaTematica, on_delete=models.PROTECT, related_name= "trabalhos", null=False, verbose_name=_("Área Temática"))
    titulo = models.CharField(max_length=250, verbose_name=_("Título"), null=False)
    tipo_chamada = models.ForeignKey(TipoChamada, on_delete=models.PROTECT,  null=False, related_name='trabalhos')
    autor_principal = models.ForeignKey(User, on_delete=models.PROTECT, null=False, related_name='trabalhos_autor_principal')
    coautores = models.ManyToManyField(User, related_name='trabalhos_coautores', verbose_name=_("Coautores"), blank=True) 
    status = models.CharField(max_length=50, choices=StatusTrabalho.choices, default=StatusTrabalho.RASCUNHO)
    #Campos Opcionais
    descricao = models.CharField(max_length=3000, null=True, verbose_name=_("Descrição"))
    resumo = models.CharField(max_length=3000, null=True, verbose_name=_("Resumo"))
    palavras_chave = models.CharField(max_length=100,  null=True, verbose_name=_("Palavras-chave"))
    slug = models.SlugField(max_length=250, null=True, unique=True)

    def __str__(self):
        return self.titulo
    
    @property
    def autores(self):
        autores = [self.autor_principal] 
        autores += list(self.coautores.all()) 
        return autores
    
    @property
    def autores_string(self):
        autores = f'{self.autor_principal.email}'
        if self.coautores.count() > 0:
            autores = f'{autores}, {", ".join([autor.email for autor in self.coautores.all()])}'
        return autores
    
    
    @property
    def submissoes_p_etapa(self):
        submissoes = []
        for chamada in self.tipo_chamada.lista_chamadas:
            submissao = self.submissoes.filter(chamada=chamada).first()
            if not submissao:
                submissao = Submissao.objects.create(trabalho=self, chamada=chamada, documento=documento)
            submissoes.append(submissao)
        return submissoes
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

        
class StatusAvaliacao(models.TextChoices):
    AVALIACAO_SOLICITADA = 'SOLICITADA', _('Aguardando Avaliação')
    AVALIACAO_CANCELADA = 'CANCELADA', _('Cancelada Avaliação')
    EM_AVALIACAO= "EM_AVALIACAO", _('Em Avaliação')
    CONCLUIDA = 'CONCLUIDA', _('Concluida')
    ACEITO = 'ACEITO', _('Aceito')
    RECUSADO = 'RECUSADO', _('Recusado')
    ACEITO_C_RESSALVAS = 'ACEITO_C_RESSALVAS', _('Aceito com Ressalvas')   
    APRESENTADO = 'APRESENTADO', _('Apresentado')
    NAO_APRESENTADO = 'NAO_APRESENTADO', _('Não Apresentado')

class Submissao(models.Model):
    trabalho = models.ForeignKey(Trabalho, on_delete=models.CASCADE, related_name='submissoes', null=False)
    chamada = models.ForeignKey(Chamada, on_delete=models.CASCADE, related_name='submissoes', null=False)
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        null=True,
        related_name='submissoes',
        verbose_name=_("Documento")
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    
    nota_final = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Nota Avaliação")
    )

    status_avaliacao = models.CharField(max_length=50, choices=StatusAvaliacao.choices,default=StatusAvaliacao.AVALIACAO_SOLICITADA, null=True)
    
    def __str__(self):
        return f"{self.documento} da etapa {self.chamada}"
    
    def processar_avaliacao(self):

        # so processa se o trabalho estiver submetido
        if self.trabalho.status == StatusTrabalho.RASCUNHO:
            return  
        
        #so processa se chamada estiver encerrada
        if self.chamada.status != StatusChamada.ENCERRADO:
            return
        
        total_avaliacoes = self.avaliacoes_realizadas.count()
        # Verifica se o total de avaliações é menor que o mínimo exigido pela chamada
        if total_avaliacoes < self.chamada.min_avaliacoes:
            self.status_avaliacao = StatusAvaliacao.AVALIACAO_SOLICITADA
            self.nota_final = 0
            self.trabalho.status = StatusTrabalho.EM_AVALIACAO
            self.trabalho.save()
            self.save()
            return  

        
        if self.chamada.forma_avaliacao != FormaAvaliacao.SEM:
            if self.chamada.etapa == EtapaChamada.INICIAL:
                # Conta as avaliações aceitas, aceitas com ressalvas e recusadas
                count_aceitos = self.avaliacoes_realizadas.filter(status=StatusAvaliacao.ACEITO).count()
                count_aceitos_c_res = self.avaliacoes_realizadas.filter(status=StatusAvaliacao.ACEITO_C_RESSALVAS).count()
                count_recusados = self.avaliacoes_realizadas.filter(status=StatusAvaliacao.RECUSADO).count()

                # Verifica se o número de recusados é maior que aceitos + aceitos com ressalvas
                if count_recusados > (count_aceitos + count_aceitos_c_res):
                    self.status_avaliacao = StatusAvaliacao.RECUSADO
                    self.trabalho.status = StatusTrabalho.REPROVADO
                    self.nota_final = 0
                else:
                    # Caso contrário, o trabalho é aprovado
                    self.trabalho.status = StatusTrabalho.APROVADO
                    
                    # Verifica se existe pelo menos um aceito com ressalvas
                    if count_aceitos_c_res > 0:
                        self.status_avaliacao = StatusAvaliacao.ACEITO_C_RESSALVAS
                    else:
                        self.status_avaliacao = StatusAvaliacao.ACEITO

                    # Calcula a nota final com base nas notas parciais das avaliações
                    total_nota = self.avaliacoes_realizadas.filter(
                        Q(status=StatusAvaliacao.ACEITO) | 
                        Q(status=StatusAvaliacao.ACEITO_C_RESSALVAS) |
                        Q(status=StatusAvaliacao.RECUSADO)
                    ).aggregate(Sum('nota_parcial'))['nota_parcial__sum'] or 0
                    
                    # Atualiza a nota final se houver avaliações
                    if total_avaliacoes > 0:
                        self.nota_final = total_nota / total_avaliacoes
                    else:
                        self.nota_final = 0

            # Etapa de Apresentação
            elif self.chamada.etapa == EtapaChamada.APRESENTACAO:
                total_apresentou = self.avaliacoes_realizadas.filter(status=StatusAvaliacao.APRESENTADO).count()
                if total_apresentou > 0:
                    # Se houver pelo menos uma apresentação, calcula a nota final com base nas avaliações apresentadas
                    total_nota_apresentada = self.avaliacoes_realizadas.filter(status=StatusAvaliacao.APRESENTADO).aggregate(Sum('nota_parcial'))['nota_parcial__sum'] or 0
                    self.nota_final = total_nota_apresentada / total_apresentou
                    self.status_avaliacao = StatusAvaliacao.APRESENTADO
                    self.trabalho.status = StatusTrabalho.APRESENTADO
                else:
                    # Caso não haja apresentações, marca como não apresentado e zera a nota
                    self.nota_final = 0
                    self.status_avaliacao = StatusAvaliacao.NAO_APRESENTADO
                    self.trabalho.status = StatusTrabalho.N_APRESENTADO

            # Etapa Final
            elif self.chamada.etapa == EtapaChamada.FINAL:
                # Soma todas as notas parciais das avaliações
                total_nota_final = self.avaliacoes_realizadas.aggregate(Sum('nota_parcial'))['nota_parcial__sum'] or 0
                self.nota_final = total_nota_final / total_avaliacoes
                # Define o status da avaliação como 'CONCLUIDA'
                self.status_avaliacao = StatusAvaliacao.CONCLUIDA

            # Salva o status do trabalho
            self.trabalho.save()

        # Caso a forma de avaliação seja 'SEM', aplica o status 'CONCLUIDA'
        else:
            self.nota_final = 0
            self.status_avaliacao = StatusAvaliacao.CONCLUIDA

        # Salva as alterações na submissão
        self.save()


    
    @property
    def get_status(self):
        status_avaliacao_choice = StatusAvaliacao(self.status_avaliacao)
        return status_avaliacao_choice.label
    
    @property
    def avaliacoes_realizadas(self):
        avaliacoes = Avaliacao.objects.filter(submissao=self, status__in=[StatusAvaliacao.CONCLUIDA, StatusAvaliacao.ACEITO, StatusAvaliacao.ACEITO_C_RESSALVAS, StatusAvaliacao.RECUSADO, StatusAvaliacao.APRESENTADO, StatusAvaliacao.NAO_APRESENTADO])        
        return avaliacoes
        
    
    class Meta:
        verbose_name = _("Submissão")
        verbose_name_plural = _("Submissões")

class Avaliacao(models.Model):
    submissao = models.ForeignKey(Submissao, on_delete=models.CASCADE, related_name='avaliacoes')
    avaliador = models.ForeignKey(Avaliador, on_delete=models.CASCADE, related_name='avaliacoes')
    status = models.CharField(max_length=50, choices=StatusAvaliacao.choices, null=False, default=StatusAvaliacao.AVALIACAO_SOLICITADA)    
    nota_parcial = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dt_limite_aceite = models.DateField(null=False, default= get_hoje, validators=[validate_future_date],verbose_name=_("Data Limite de Aceite"))
    comentario = models.TextField(max_length=200, blank=True, null=True, verbose_name=_("Comentário Geral"))

    def save(self, *args, **kwargs):
        if self.status == StatusAvaliacao.AVALIACAO_CANCELADA or (
            self.status == StatusAvaliacao.CONCLUIDA 
            and self.submissao.chamada.forma_avaliacao == FormaAvaliacao.SEM):
                self.avaliacoes_criterios.all().delete()
                self.nota_parcial = 0
        else:
            notas = self.avaliacoes_criterios.all() if self.id else []
            if len(notas) == 0:
                self.nota_parcial = None    
            elif self.submissao.chamada.forma_avaliacao == FormaAvaliacao.SOMA:
                self.nota_parcial = self.__soma()
            elif (self.submissao.chamada.forma_avaliacao == FormaAvaliacao.MEDIA_PONDERADA 
                    or self.submissao.chamada.forma_avaliacao == FormaAvaliacao.MEDIA_ARITMETICA):
                self.nota_parcial = self.__media()
            else:
                self.nota_parcial = 0
        super().save(*args, **kwargs)
        

    def __media(self):
        """Calcula a média ponderada das notas dos critérios."""
        avaliacao_p_criterio = AvaliacaoCriterio.objects.filter(avaliacao=self)
        notas = []
        pesos = []
        for ac in avaliacao_p_criterio:
            nota = ac.nota_criterio * ac.criterio.peso if ac.nota_criterio else 0
            notas.append(nota)
            pesos.append(ac.criterio.peso)
        nota_parcial = sum(notas)/sum(pesos)
        return nota_parcial

    def __soma(self):
        """Calcula a soma simples das notas dos critérios."""
        avaliacao_p_criterio = AvaliacaoCriterio.objects.filter(avaliacao=self)
        nota = 0
        for ac in avaliacao_p_criterio:
            nota += ac.nota_criterio
        return nota
    
    @property
    def nota_criterios(self):
        nc = []
        for ac in self.avaliacoes_criterios.all():
            nc.append(f'{ac.criterio.nome}:{ac.nota_criterio}')
            
        return ",".join(nc)
    
    def __str__(self):
        return f"{self.avaliador} - {self.submissao}"
    
    @property
    def criterios_detail(self):
        nc = []
        for ac in self.avaliacoes_criterios.all():
            criterio =format_html(f'<div class="col"><b>{ac.criterio.nome}</b>:{ac.nota_criterio}<br/>{ac.comentario}</div>') 
            nc.append(criterio)
        nc = " ".join(nc).strip()
        return format_html(f'<div class="row row-cols-md-5 row-cols-2">{nc}</div>')

    class Meta:
        verbose_name = _("Avaliação")
        verbose_name_plural = _("Avaliações")
        
class AvaliacaoCriterio(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='avaliacoes_criterios', null=False)
    criterio = models.ForeignKey(CriterioAvaliacao,  on_delete=models.CASCADE, related_name='avaliacoes_criterios', null=False)
    nota_criterio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Nota"))
    comentario = models.TextField(max_length=100, blank=True, null=True, verbose_name=_("Comentário"))

    class Meta:
        verbose_name = _("Avaliação de Critério")
        verbose_name_plural = _("Avaliações de Critérios")

    def __str__(self):
        return f"{self.avaliacao.submissao.trabalho.titulo} - {self.criterio.nome}: {self.nota_criterio}"

@receiver(post_save, sender=Avaliacao)
def atualizar_status_trabalho_on_save_avaliacao(
    sender, instance: Avaliacao, created, raw: bool = False, *args, **kwargs
):
    if not created:
        instance.submissao.processar_avaliacao()

@receiver(post_delete, sender=Avaliacao)
def atualizar_status_trabalho_on_delete_avaliacao(
    sender, instance: Avaliacao, *args, **kwargs
):
    instance.submissao.processar_avaliacao()

@receiver(post_save, sender=AvaliacaoCriterio)
def atualizar_nota_avaliacao_on_save_criterio(
    sender, instance: AvaliacaoCriterio, created, raw: bool = False, *args, **kwargs
):
    if not created:
        instance.avaliacao.save()
