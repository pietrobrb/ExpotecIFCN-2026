
document.addEventListener("DOMContentLoaded", () => {
  const busca = document.getElementById("busca-atividades");
  const cards = [...document.querySelectorAll("[data-atividade]")];
  const contador = document.getElementById("contador-atividades");
  const vazio = document.getElementById("busca-sem-resultados");

  function filtrarAtividades() {
    const termo = (busca?.value || "").trim().toLocaleLowerCase("pt-BR");
    let visiveis = 0;

    cards.forEach((card) => {
      const texto = [
        card.dataset.titulo,
        card.dataset.descricao,
        card.dataset.local,
        card.dataset.tipo,
      ].join(" ");

      const corresponde = texto.includes(termo);
      card.hidden = !corresponde;

      if (corresponde) visiveis++;
    });

    if (contador) {
      contador.textContent =
        `${visiveis} atividade(s) correspondente(s) nesta página.`;
    }

    if (vazio) {
      vazio.hidden = visiveis !== 0 || cards.length === 0;
    }
  }

  busca?.addEventListener("input", filtrarAtividades);

  function atualizarBotoesAgenda() {
    const agenda = window.ExpotecAgenda;
    if (!agenda || typeof agenda.ids !== "function") return;

    const ids = agenda.ids().map(String);

    document.querySelectorAll("[data-alternar-agenda]").forEach((botao) => {
      const salvo = ids.includes(String(botao.dataset.alternarAgenda));

      botao.setAttribute("aria-pressed", String(salvo));
      botao.textContent = salvo ? "✓ Na minha agenda" : "+ Minha agenda";
    });
  }

  document.querySelectorAll("[data-alternar-agenda]").forEach((botao) => {
    botao.addEventListener("click", () => {
      const agenda = window.ExpotecAgenda;

      if (!agenda || typeof agenda.alternar !== "function") {
        alert("Não foi possível carregar a agenda pessoal. Atualize a página e tente novamente.");
        return;
      }

      agenda.alternar(String(botao.dataset.alternarAgenda));

      if (typeof agenda.atualizarContadores === "function") {
        agenda.atualizarContadores();
      }

      atualizarBotoesAgenda();
    });
  });

  filtrarAtividades();
  atualizarBotoesAgenda();
});
