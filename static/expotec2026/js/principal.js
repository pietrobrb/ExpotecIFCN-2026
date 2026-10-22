document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  document
    .querySelectorAll("[data-nav]")
    .forEach((link) =>
      link.classList.toggle("active", link.dataset.nav === page),
    );
});
