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

// "Não tenho disponibilidade": desmarca e desabilita as datas quando ativo
const semDisp = document.getElementById("sem-disponibilidade");
if (semDisp) {
  const dateBoxes = document.querySelectorAll('.datas-check input[type="checkbox"]');
  const sync = () => {
    dateBoxes.forEach((b) => {
      if (semDisp.checked) {
        b.checked = false;
        b.disabled = true;
      } else {
        b.disabled = false;
      }
    });
  };
  semDisp.addEventListener("change", sync);
  sync();
}

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
