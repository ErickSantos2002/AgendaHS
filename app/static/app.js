// Copiar link para a área de transferência
document.querySelectorAll(".copiar").forEach((btn) => {
  btn.addEventListener("click", () => {
    const alvo = document.getElementById(btn.dataset.alvo);
    if (!alvo) return;
    alvo.select();
    navigator.clipboard.writeText(alvo.value).then(() => {
      const original = btn.textContent;
      btn.textContent = "copiado!";
      setTimeout(() => (btn.textContent = original), 1500);
    });
  });
});

// Adicionar novas linhas de data no formulário de criar evento
const addBtn = document.getElementById("add-data");
if (addBtn) {
  addBtn.addEventListener("click", () => {
    const container = document.getElementById("datas");
    const linha = document.createElement("div");
    linha.className = "linha-data";
    linha.innerHTML =
      '<input type="date" name="data">' +
      '<input type="time" name="horario">';
    container.appendChild(linha);
  });
}
