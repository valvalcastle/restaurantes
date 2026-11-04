// FriendlyEats: crear, editar y eliminar restaurantes contra /api/v1
(() => {
  const messageBox = document.getElementById("message");

  function showMessage(text, type) {
    if (!messageBox) return;
    messageBox.textContent = text;
    messageBox.className = `message ${type}`;
    messageBox.hidden = false;
    messageBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // FastAPI devuelve {detail: "texto"} o {detail: [{loc, msg}, ...]} (errores 422).
  async function readError(response) {
    let body = null;
    try {
      body = await response.json();
    } catch (_) {}
    const detail = body && body.detail;
    if (Array.isArray(detail)) {
      return detail
        .map((e) => `${(e.loc || []).slice(-1)[0]}: ${e.msg}`)
        .join("; ");
    }
    return detail || "No se pudo guardar. Intenta de nuevo.";
  }

  // --- Formulario crear / editar ---
  const form = document.getElementById("restaurant-form");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const isEdit = form.dataset.mode === "edit";
      const submit = form.querySelector("button[type=submit]");

      const data = Object.fromEntries(new FormData(form));
      data.price = Number(data.price);
      data.photoUrl = (data.photoUrl || "").trim() || null;

      const url = isEdit
        ? `/api/v1/restaurants/${form.dataset.id}`
        : "/api/v1/restaurants";

      submit.disabled = true;
      try {
        const response = await fetch(url, {
          method: isEdit ? "PATCH" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        if (!response.ok) {
          showMessage(await readError(response), "error");
          return;
        }
        const saved = await response.json();
        showMessage(isEdit ? "Cambios guardados." : "Restaurante creado correctamente.", "ok");
        const flash = isEdit ? "updated" : "created";
        setTimeout(() => {
          window.location.href = `/restaurants/${saved.id}?msg=${flash}`;
        }, 600);
      } catch (_) {
        showMessage("No se pudo conectar con el servidor.", "error");
      } finally {
        submit.disabled = false;
      }
    });
  }

  // --- Botón eliminar (con confirmación) ---
  document.querySelectorAll("[data-delete-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      const name = button.dataset.name;
      if (!window.confirm(`¿Eliminar "${name}"? Esta acción no se puede deshacer.`)) return;

      button.disabled = true;
      try {
        const response = await fetch(`/api/v1/restaurants/${button.dataset.deleteId}`, {
          method: "DELETE",
        });
        if (response.status === 204) {
          window.location.href = "/?msg=deleted"; // el listado se recarga actualizado
          return;
        }
        showMessage(await readError(response), "error");
      } catch (_) {
        showMessage("No se pudo conectar con el servidor.", "error");
      }
      button.disabled = false;
    });
  });
})();
