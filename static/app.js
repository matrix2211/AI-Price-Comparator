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

async function search() {
  const q = document.getElementById("query").value.trim();
  if (!q) return;

  const carousel = document.getElementById("carousel");
  const hint = document.getElementById("scrollHint");

  carousel.innerHTML = "";
  carousel.classList.remove("hidden");
  hint.classList.remove("hidden");

  const res = await fetch(`/compare?query=${encodeURIComponent(q)}`);
  const data = await res.json();

  data.forEach((group, idx) => {
    const slide = document.createElement("div");
    slide.className = "slide";

    let offersHTML = "";
    group.offers.forEach(o => {
      offersHTML += `
        <div class="offer">
          <span>${o.source}</span>
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

  // Hide scroll hint after first scroll
  carousel.addEventListener("scroll", () => {
    hint.classList.add("hidden");
  }, { once: true });

  carousel.scrollTo({ top: 0, behavior: "smooth" });
}
