let scannerStream = null;
let scannerFrame = null;
let lastScanAt = 0;

function aviso(texto) {
  const box = document.querySelector(".toast");
  if (!box) return;
  box.textContent = texto;
  box.classList.add("show");
  setTimeout(() => box.classList.remove("show"), 2800);
}
function pararCamera() {
  if (scannerFrame) cancelAnimationFrame(scannerFrame);
  scannerFrame = null;
  if (scannerStream) scannerStream.getTracks().forEach((track) => track.stop());
  scannerStream = null;
  const video = document.querySelector("#qr-video");
  if (video) video.srcObject = null;
}
function fecharLeitor() {
  pararCamera();
  document.querySelector("#scanner-panel").hidden = true;
}

async function abrirLeitor() {
  const panel = document.querySelector("#scanner-panel"),
    video = document.querySelector("#qr-video"),
    status = document.querySelector("#scanner-status"),
    result = document.querySelector("#qr-result");
  panel.hidden = false;
  result.hidden = true;
  status.textContent = "Solicitando acesso à câmera…";
  panel.scrollIntoView({ behavior: "smooth", block: "center" });
  if (!navigator.mediaDevices?.getUserMedia) {
    status.textContent =
      "Este navegador não permite abrir a câmera. Use a câmera normal do celular.";
    return;
  }
  try {
    scannerStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } },
      audio: false,
    });
    video.srcObject = scannerStream;
    await video.play();
    if (!("BarcodeDetector" in window)) {
      status.textContent =
        "A câmera abriu, mas este navegador não possui leitor integrado. Use a câmera normal do celular.";
      return;
    }
    const detector = new BarcodeDetector({ formats: ["qr_code"] });
    status.textContent = "Aponte a câmera para o QR Code da atividade.";
    const detectar = async (agora) => {
      if (!scannerStream) return;
      if (agora - lastScanAt > 250) {
        lastScanAt = agora;
        try {
          const codes = await detector.detect(video);
          if (codes.length) {
            pararCamera();
            status.textContent =
              "QR Code lido. Entre com o SUAP para validar a presença.";
            result.hidden = false;
            return;
          }
        } catch {}
      }
      scannerFrame = requestAnimationFrame(detectar);
    };
    scannerFrame = requestAnimationFrame(detectar);
  } catch (error) {
    pararCamera();
    status.textContent =
      error?.name === "NotAllowedError"
        ? "A câmera não foi autorizada. Permita o acesso ou use a câmera normal."
        : "Não foi possível abrir a câmera.";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelector("#scan-qr-button")
    ?.addEventListener("click", abrirLeitor);
  document
    .querySelector("#close-scanner")
    ?.addEventListener("click", fecharLeitor);
  document
    .querySelector("#attendance-button")
    ?.addEventListener("click", () =>
      aviso("O login será conectado pela equipe de backend."),
    );
  document
    .querySelector("#qr-login-button")
    ?.addEventListener("click", () =>
      aviso("O login será conectado pela equipe de backend."),
    );
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) pararCamera();
});
