function toggleTheme() {
  document.body.classList.toggle("dark");
  localStorage.setItem(
    "theme",
    document.body.classList.contains("dark") ? "dark" : "light"
  );
}

window.onload = () => {
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark");
  }
};

/* 🔑 THIS WAS THE MISSING PIECE */
function quickSearch(text) {
  const input = document.getElementById("query");
  if (!input) return;

  input.value = text;
  input.focus();
  search();
}

async function search() {
  const q = document.getElementById("query").value.trim();
  if (!q) return;

  const carousel = document.getElementById("carousel");
  carousel.innerHTML = "";
  carousel.classList.remove("hidden");

  const res = await fetch(`/compare?query=${encodeURIComponent(q)}`);
  const data = await res.json();

  data.forEach(group => {
    const slide = document.createElement("div");
    slide.className = "slide";

    let offersHTML = "";

    group.offers.forEach(o => {
      const seller = o.link
        ? `<a href="${o.link}" target="_blank" rel="noopener noreferrer">${o.source}</a>`
        : o.source;

      offersHTML += `
        <div class="offer">
          <span class="seller">${seller}</span>
          <strong>₹${o.price}</strong>
        </div>
      `;
    });

    slide.innerHTML = `
      <div class="card best">
        <div class="best-tag">BEST DEAL</div>
        <h2>${group.product}</h2>
        ${offersHTML}
        <p class="verdict">${group.verdict}</p>
      </div>
    `;

    carousel.appendChild(slide);
  });
}
