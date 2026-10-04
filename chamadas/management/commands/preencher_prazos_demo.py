"""Preenche um Tipo de Chamada JÁ EXISTENTE com prazos (etapas) fictícios.

Serve para a página pública do tipo (portal/templates/chamada_detail.html),
que lista `tipo.lista_chamadas` em "Prazos" e `tipo.tipo_chamada_documentos`
em "Documentos". Não cria tipos nem altera o nome/descrição do tipo.

Uso:
    python manage.py preencher_prazos_demo --tipo-nome "Inscreva-se"
    python manage.py preencher_prazos_demo --tipo-id 7
    python manage.py preencher_prazos_demo --tipo-nome "Inscreva-se" --com-documentos

Todos os dados são FICTÍCIOS. As datas são relativas a hoje, então a
demonstração sempre mostra os status Aberto e Em Breve.

Pode ser rodado várias vezes: atualiza as chamadas da mesma etapa em vez de
duplicar. Para remover, apague as chamadas desse tipo no admin do Django.
"""
import datetime

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import get_hoje

from chamadas.models import (
    Chamada,
    CriterioAvaliacao,
    EtapaChamada,
    FormaAvaliacao,
    TipoChamada,
    TipoChamadaDocumento,
)


def dias(n):
    return get_hoje() + datetime.timedelta(days=n)


def chamadas_demo():
    """Prazos fictícios. Edite aqui para mudar a demonstração."""
    return [
        {
            "etapa": EtapaChamada.INICIAL,
            "inicio": dias(-18),
            "fim": dias(12),
            "tem_submissao": True,
            "forma_avaliacao": FormaAvaliacao.MEDIA_PONDERADA,
            "min_avaliacoes": 2,
            "min_aprovacoes": 1,
            "criterios": [
                ("Relevância", "Importância do tema (demo)", 3),
                ("Metodologia", "Clareza do método (demo)", 3),
                ("Clareza", "Qualidade do texto (demo)", 2),
                ("Originalidade", "Novidade da proposta (demo)", 2),
            ],
        },
        {
            "etapa": EtapaChamada.APRESENTACAO,
            "inicio": dias(17),
            "fim": dias(27),
            "tem_submissao": False,
            "forma_avaliacao": FormaAvaliacao.SEM,
            "min_avaliacoes": 0,
            "min_aprovacoes": 1,
            "criterios": [],
        },
        {
            "etapa": EtapaChamada.FINAL,
            "inicio": dias(29),
            "fim": dias(38),
            "tem_submissao": True,
            "forma_avaliacao": FormaAvaliacao.MEDIA_ARITMETICA,
            "min_avaliacoes": 2,
            "min_aprovacoes": 1,
            "criterios": [
                ("Versão final", "Atendimento às correções (demo)", 1),
                ("Formatação", "Aderência ao modelo (demo)", 1),
            ],
        },
    ]


DOCUMENTOS_DEMO = [
    ("Regulamento (demo)", "REGRA"),
    ("Modelo de resumo (demo)", "MODELO"),
]


class Command(BaseCommand):
    help = "Preenche um Tipo de Chamada existente com prazos fictícios (etapas e datas)."

    def add_arguments(self, parser):
        parser.add_argument("--tipo-id", type=int, help="ID do Tipo de Chamada.")
        parser.add_argument("--tipo-nome", help='Nome do Tipo de Chamada (ex.: "Inscreva-se").')
        parser.add_argument(
            "--com-documentos",
            action="store_true",
            help="Cria também documentos fictícios (regra e modelo) para o tipo.",
        )

    def handle(self, *args, **options):
        tipo = self.obter_tipo(options["tipo_id"], options["tipo_nome"])
        self.stdout.write(f"Tipo: {tipo.nome} (id={tipo.pk}, evento={tipo.evento})")

        with transaction.atomic():
            for c in chamadas_demo():
                chamada, criada = Chamada.objects.update_or_create(
                    tipo=tipo,
                    etapa=c["etapa"],
                    defaults={
                        "dt_inicio": c["inicio"],
                        "dt_encerramento": c["fim"],
                        "tem_submissao": c["tem_submissao"],
                        "forma_avaliacao": c["forma_avaliacao"],
                        "min_avaliacoes": c["min_avaliacoes"],
                        "min_aprovacoes": c["min_aprovacoes"],
                    },
                )
                # Chamada.save() calcula o status pelas datas.
                self.stdout.write(
                    f"  {'Criada' if criada else 'Atualizada'}: "
                    f"{chamada.get_etapa_display()} -> {chamada.get_status_display()} "
                    f"({chamada.dt_inicio:%d/%m/%Y} a {chamada.dt_encerramento:%d/%m/%Y})"
                )
                for nome, descricao, peso in c["criterios"]:
                    CriterioAvaliacao.objects.get_or_create(
                        chamada=chamada,
                        nome=nome,
                        defaults={"descricao": descricao, "peso": peso},
                    )

            if options["com_documentos"]:
                self.cadastrar_documentos(tipo)

        self.stdout.write(self.style.SUCCESS("Prazos de demonstração prontos."))

    def cadastrar_documentos(self, tipo):
        # Importado aqui para que o resto do comando funcione mesmo que o
        # model Documento tenha campos obrigatórios que eu não conheço.
        from documentos.models import Documento, TipoDocumento

        for descricao, nome_tipo in DOCUMENTOS_DEMO:
            if tipo.tipo_chamada_documentos.filter(documento__descricao=descricao).exists():
                continue
            documento = Documento.objects.create(
                descricao=descricao,
                tipo=getattr(TipoDocumento, nome_tipo),
                file=ContentFile(
                    f"{descricao} - arquivo fictício de demonstração.".encode("utf-8"),
                    name=f"{nome_tipo.lower()}_demo.txt",
                ),
            )
            TipoChamadaDocumento.objects.create(tipo_chamada=tipo, documento=documento)
            self.stdout.write(f"  Documento criado: {descricao}")

    def obter_tipo(self, tipo_id, tipo_nome):
        if tipo_id:
            try:
                return TipoChamada.objects.get(pk=tipo_id)
            except TipoChamada.DoesNotExist:
                raise CommandError(f"Não existe tipo de chamada com id={tipo_id}.")

        if tipo_nome:
            tipos = list(TipoChamada.objects.filter(nome__iexact=tipo_nome))
            if len(tipos) == 1:
                return tipos[0]
            if not tipos:
                raise CommandError(f'Nenhum tipo de chamada chamado "{tipo_nome}".')
            lista = "\n".join(f"  id={t.pk}: {t.nome} (evento: {t.evento})" for t in tipos)
            raise CommandError(f"Há mais de um tipo com esse nome; use --tipo-id.\n{lista}")

        lista = "\n".join(
            f"  id={t.pk}: {t.nome} (evento: {t.evento})" for t in TipoChamada.objects.all()
        )
        raise CommandError(f"Informe --tipo-id ou --tipo-nome. Tipos existentes:\n{lista}")