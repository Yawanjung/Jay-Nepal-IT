/**
 * jn-services.js
 * ---------------------------------------------------------------
 * services.html को सेवा-सूची /api/services/ बाट लाइभ तानिन्छ।
 * Admin बाट नयाँ सेवा थपेपछि यहाँ तुरुन्तै (refresh गरे) देखिन्छ।
 * ---------------------------------------------------------------
 */
(function () {
  "use strict";

  function buildServiceCard(service) {
    const col = document.createElement("div");
    col.className = "col-12 col-md-6 col-lg-4";
    col.innerHTML = `
      <article class="jn-feature-card">
        <div class="jn-feature-icon" aria-hidden="true">${jnEscapeHtml(service.icon_emoji) || "🛠️"}</div>
        <h3>${jnEscapeHtml(service.title)}</h3>
        <p>${jnEscapeHtml(service.summary)}</p>
        ${service.price_note ? `<p class="fw-semibold mb-0">${jnEscapeHtml(service.price_note)}</p>` : ""}
      </article>
    `;
    return col;
  }

  async function loadServices() {
    const grid = document.getElementById("jn-services-grid");
    const status = document.getElementById("jn-services-status");
    if (!grid) return;

    try {
      const response = await jnApiFetch("/services/");
      if (!response.ok) throw new Error(`services API त्रुटि: ${response.status}`);
      const data = await response.json();
      const services = data.results || [];

      grid.innerHTML = "";

      if (services.length === 0) {
        grid.innerHTML =
          '<div class="col-12"><p class="jn-news-empty">हाल कुनै सेवा थपिएको छैन। Admin बाट थप्नुहोस्।</p></div>';
        if (status) status.textContent = "कुनै सेवा फेला परेन।";
        return;
      }

      const fragment = document.createDocumentFragment();
      services.forEach((s) => fragment.appendChild(buildServiceCard(s)));
      grid.appendChild(fragment);

      if (status) status.textContent = `${services.length} सेवा देखाइँदैछ।`;
    } catch (err) {
      grid.innerHTML =
        '<div class="col-12"><p class="jn-news-empty">सेवा लोड गर्न सकिएन। Backend चलिरहेको छ कि जाँच्नुहोस्।</p></div>';
      if (status) status.textContent = "सेवा लोड गर्दा त्रुटि भयो।";
    }
  }

  document.addEventListener("DOMContentLoaded", loadServices);
})();
