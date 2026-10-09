const listElement = document.querySelector("#procedure-list");
const detailElement = document.querySelector("#detail");
const searchInput = document.querySelector("#search-input");
let procedures = [];
let selectedId = "";
let filterTimer;

const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[character]));

function renderList() {
  const query = searchInput.value.trim().toLocaleLowerCase();
  const visibleProcedures = procedures.filter((item) =>
    `${item.procedure} ${item.title} ${item.description}`.toLocaleLowerCase().includes(query));
  const groups = new Map();
  for (const procedure of visibleProcedures) {
    const letter = (procedure.procedure || "#").charAt(0).toUpperCase();
    if (!groups.has(letter)) groups.set(letter, []);
    groups.get(letter).push(procedure);
  }
  listElement.innerHTML = visibleProcedures.length ? [...groups].map(([letter, items]) => `
    <section class="letter-group" aria-label="${escapeHtml(letter)}">
      <div class="letter-heading">${escapeHtml(letter)}</div>
      ${items.map((item) => `<button class="procedure-link" type="button" data-id="${escapeHtml(item.procedure)}" aria-current="${item.procedure === selectedId}">${escapeHtml(item.procedure)}</button>`).join("")}
    </section>`).join("") : `<p class="no-results">No procedures match “${escapeHtml(searchInput.value.trim())}”.</p>`;
  document.querySelector("#list-count").textContent = query ? `${visibleProcedures.length} of ${procedures.length}` : `${procedures.length} entries`;
  document.querySelector("#procedure-count").textContent = String(procedures.length);
}

function renderDetail(procedure) {
  if (!procedure) return;
  selectedId = procedure.procedure;
  renderList();
  const isNative = procedure.kind === "native-pdb";
  const metadata = isNative ? [
    ["AUTHOR", procedure.author || "Not listed"],
    ["COPYRIGHT", procedure.copyright || "Not listed"],
    ["CREATED", procedure.date || "Not listed"],
    ["KIND", "Native PDB procedure"],
  ] : [
    ["AUTHOR", procedure.author || "Not listed"],
    ["EMAIL", procedure.authorEmail || "Not listed"],
    ["CREATED", procedure.date || "Not listed"],
    ["IMAGE TYPES", procedure.imageTypes || "Not listed"],
    ["DRAWABLE TYPES", procedure.drawableTypes || "Not listed"],
    ["KEY", procedure.shortcut || "None"],
  ];
  const renderParameters = (items) => items.length ? `<ul class="parameter-list">${items.map((parameter) => `
    <li class="parameter">
      <span class="parameter-type">${escapeHtml(parameter.type)}</span>
      <span><span class="parameter-label">${escapeHtml(parameter.label || "Unlabeled")}</span>${parameter.description ? `<span class="parameter-description">${escapeHtml(parameter.description)}</span>` : ""}${parameter.details.length ? `<span class="parameter-detail">${escapeHtml(parameter.details.join(" · "))}</span>` : ""}</span>
    </li>`).join("")}</ul>` : `<p class="no-parameters">No ${isNative ? "arguments or return values" : "selectable parameters"} are defined.</p>`;
  detailElement.innerHTML = `
    <article class="procedure-detail">
      <div class="detail-topline">
        <p class="eyebrow">PROCEDURE DETAILS</p>
        <a class="source-link" href="${escapeHtml(procedure.source)}" target="_blank" rel="noopener noreferrer">View source <span aria-hidden="true">↗</span></a>
      </div>
      <h2 class="procedure-title">${escapeHtml(procedure.title || procedure.procedure)}</h2>
      <p class="procedure-name">${escapeHtml(procedure.procedure)}</p>
      <p class="summary">${escapeHtml(procedure.description || "No summary is provided in the source script.")}</p>
      <div class="metadata">${metadata.map(([label, value]) => `<div class="meta-cell"><span class="meta-label">${label}</span><span class="meta-value">${escapeHtml(value)}</span></div>`).join("")}</div>
      <h3 class="section-heading">Where can I find this in Gimp's Menu?</h3>
      <div class="menu-location"><code>${escapeHtml(procedure.menuPath || "No menu item registered")}</code><p>${procedure.menuPath ? "Menu location in GIMP" : "Available through the GIMP Procedure Database"}</p></div>
      <h3 class="section-heading">${isNative ? "Arguments" : "Selectable parameters"} <span>${procedure.parameters.length} FIELDS</span></h3>
      ${renderParameters(procedure.parameters)}
      ${isNative ? `<h3 class="section-heading">Return values <span>${procedure.returnValues.length} FIELDS</span></h3>${renderParameters(procedure.returnValues)}` : ""}
    </article>`;
  const current = listElement.querySelector(`[data-id="${CSS.escape(selectedId)}"]`);
  current?.scrollIntoView({ block: "nearest" });
}

listElement.addEventListener("click", (event) => {
  const button = event.target.closest("[data-id]");
  if (button) renderDetail(procedures.find((item) => item.procedure === button.dataset.id));
});
searchInput.addEventListener("input", () => {
  clearTimeout(filterTimer);
  filterTimer = setTimeout(renderList, 120);
});
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    searchInput.focus();
  }
});

fetch("data/pdb.json")
  .then((response) => {
    if (!response.ok) throw new Error("The generated catalog is not available.");
    return response.json();
  })
  .then((data) => {
    procedures = data.procedures || [];
    if (!procedures.length) throw new Error("No Script-Fu procedures were found in the catalog.");
    renderList();
    renderDetail(procedures[0]);
  })
  .catch(() => {
    listElement.innerHTML = `<p class="loading">Catalog data could not be loaded. Run the build script or use the published Pages site.</p>`;
    document.querySelector("#procedure-count").textContent = "0";
  });