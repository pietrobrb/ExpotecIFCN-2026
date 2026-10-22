
document.addEventListener("DOMContentLoaded", async () => {
    const raiz = document.getElementById("minha-agenda");
    const lista = document.getElementById("minha-agenda-lista");
    const vazio = document.getElementById("minha-agenda-vazia");
    const limpar = document.getElementById("limpar-minha-agenda");
    const chave = "expotecAgenda";

    function obterIds() {
        try {
            const dados = JSON.parse(localStorage.getItem(chave) || "[]");
            return Array.isArray(dados) ? dados.map(String) : [];
        } catch {
            return [];
        }
    }

    function salvarIds(ids) {
        localStorage.setItem(chave, JSON.stringify(ids));

        if (window.ExpotecAgenda?.ids) {
            window.ExpotecAgenda.ids.clear();
            ids.forEach((id) => window.ExpotecAgenda.ids.add(id));
            window.ExpotecAgenda.atualizarContadores();
        } else {
            document.querySelectorAll(".agenda-count").forEach((el) => {
                el.textContent = ids.length;
            });
        }
    }

    function criarElemento(tag, classe, texto) {
        const elemento = document.createElement(tag);
        if (classe) elemento.className = classe;
        if (texto !== undefined) elemento.textContent = texto;
        return elemento;
    }

    function renderizar(atividades) {
        const ids = obterIds();
        const selecionadas = atividades.filter((a) => ids.includes(String(a.id)));

        lista.replaceChildren();
        lista.hidden = selecionadas.length === 0;
        vazio.hidden = selecionadas.length !== 0;

        document.querySelectorAll(".agenda-count").forEach((el) => {
            el.textContent = ids.length;
        });

        selecionadas.forEach((atividade) => {
            const card = criarElemento("article", "atividade-card");
            card.style.setProperty("--atividade-cor", atividade.cor || "#087849");

            const horario = criarElemento("div", "atividade-card__horario");
            horario.append(
                criarElemento("strong", "", atividade.inicio),
                criarElemento("span", "", `até ${atividade.fim}`)
            );

            const conteudo = criarElemento("div", "atividade-card__conteudo");
            conteudo.append(
                criarElemento("span", "atividade-card__tipo", atividade.tipo),
                criarElemento("h2", "", atividade.titulo),
                criarElemento(
                    "p",
                    "atividade-card__descricao",
                    atividade.descricao
                )
            );

            const detalhes = criarElemento("div", "atividade-card__detalhes");
            detalhes.append(
                criarElemento("span", "", `Data: ${atividade.dia}`),
                criarElemento("span", "", `Local: ${atividade.local}`)
            );
            conteudo.append(detalhes);

            const botao = criarElemento(
                "button",
                "atividade-card__agenda",
                "Remover da agenda"
            );
            botao.type = "button";

            botao.addEventListener("click", () => {
                const atualizados = obterIds().filter(
                    (id) => id !== String(atividade.id)
                );
                salvarIds(atualizados);
                renderizar(atividades);
            });

            card.append(horario, conteudo, botao);
            lista.appendChild(card);
        });

        if (selecionadas.length === 0) {
            vazio.hidden = false;
        }
    }

    try {
        lista.hidden = false;
        lista.textContent = "Carregando atividades...";

        const resposta = await fetch(raiz.dataset.apiUrl);

        if (!resposta.ok) {
            throw new Error(`Falha ao consultar programação: HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();
        const atividades = dados.atividades || [];

        renderizar(atividades);

        limpar?.addEventListener("click", () => {
            salvarIds([]);
            renderizar(atividades);
        });
    } catch (erro) {
        console.error("Erro ao carregar agenda:", erro);
        lista.replaceChildren(
            criarElemento(
                "p",
                "",
                "Não foi possível carregar as atividades. Atualize a página e tente novamente."
            )
        );
        lista.hidden = false;
    }
});
