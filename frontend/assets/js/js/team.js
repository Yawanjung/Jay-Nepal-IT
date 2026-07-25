(function () {
  "use strict";

  function buildTeamCard(member) {
    const col = document.createElement("div");
    col.className = "col-12 col-md-4";

    const avatarHtml = member.avatar_url
      ? `<img class="jn-avatar jn-avatar-img" src="${member.avatar_url}" alt="${member.name} को फोटो" />`
      : `<div class="jn-avatar" aria-hidden="true">${member.initials}</div>`;

    const portfolioHtml = member.portfolio_url
      ? `<a class="jn-portfolio-link" href="${member.portfolio_url}" target="_blank" rel="noopener noreferrer">
           पोर्टफोलियो हेर्नुहोस् <span class="visually-hidden">— ${member.name} (नयाँ ट्याबमा खुल्छ)</span>
         </a>`
      : "";

    col.innerHTML = `
      <article class="jn-team-card">
        ${avatarHtml}
        <h3>${member.name}</h3>
        <span class="jn-role">${member.role}</span>
        ${member.bio ? `<p class="jn-bio">${member.bio}</p>` : ""}
        ${portfolioHtml}
      </article>
    `;
    return col;
  }

  async function loadTeam() {
    const grid = document.getElementById("jn-team-grid");
    const status = document.getElementById("jn-team-status");
    if (!grid) return;

    try {
      const response = await jnApiFetch("/team/");
      if (!response.ok) throw new Error(`team API त्रुटि: ${response.status}`);
      const data = await response.json();
      const members = data.results || [];

      grid.innerHTML = "";

      if (members.length === 0) {
        grid.innerHTML =
          '<div class="col-12"><p class="jn-news-empty">हाल कुनै टोली सदस्य थपिएको छैन।</p></div>';
        if (status) status.textContent = "कुनै टोली सदस्य फेला परेन।";
        return;
      }

      const fragment = document.createDocumentFragment();
      members.forEach((m) => fragment.appendChild(buildTeamCard(m)));
      grid.appendChild(fragment);

      if (status) status.textContent = `${members.length} टोली सदस्य देखाइँदैछ।`;
    } catch (err) {
      grid.innerHTML =
        '<div class="col-12"><p class="jn-news-empty">टोली लोड गर्न सकिएन। Backend चलिरहेको छ कि जाँच्नुहोस्।</p></div>';
      if (status) status.textContent = "टोली लोड गर्दा त्रुटि भयो।";
    }
  }

  document.addEventListener("DOMContentLoaded", loadTeam);
})();
