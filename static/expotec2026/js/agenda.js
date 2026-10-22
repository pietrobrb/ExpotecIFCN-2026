const AGENDA_KEY = "expotecAgenda";
const agendaIds = new Set(JSON.parse(localStorage.getItem(AGENDA_KEY) || "[]"));

function atualizarContadores() {
  document
    .querySelectorAll(".agenda-count")
    .forEach((el) => (el.textContent = agendaIds.size));
}

function salvarAgenda() {
  localStorage.setItem(AGENDA_KEY, JSON.stringify([...agendaIds]));
  atualizarContadores();
}

window.ExpotecAgenda = {
  ids: agendaIds,
  alternar(id) {
    agendaIds.has(id) ? agendaIds.delete(id) : agendaIds.add(id);
    salvarAgenda();
  },
  limpar() {
    agendaIds.clear();
    salvarAgenda();
  },
  atualizarContadores,
};

document.addEventListener("DOMContentLoaded", atualizarContadores);
