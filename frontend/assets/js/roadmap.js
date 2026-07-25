/**
 * jn-roadmap.js
 * ---------------------------------------------------------------
 * "आगामी योजना र सक्रिय सुविधाहरू" बोर्ड — डाइनामिक रोडम्याप रेन्डरर।
 * डेटा /api/roadmap/ बाट (Django backend) लाइभ तानिन्छ।
 * ---------------------------------------------------------------
 */
(function () {
  "use strict";

  const STATUS_META = {
    planned: { label: "योजनामा", badgeClass: "jn-badge-planned" },
    progress: { label: "विकासमा", badgeClass: "jn-badge-progress" },
    testing: { label: "परीक्षणमा", badgeClass: "jn-badge-testing" },
    active: { label: "सक्रिय", badgeClass: "jn-badge-active" },
  };

  async function FETCH_ROADMAP_DATA() {
    const response = await jnApiFetch("/roadmap/");
    if (!response.ok) {
      throw new Error(`रोडम्याप API त्रुटि: ${response.status}`);
    }
    const data = await response.json();
    return data.results || [];
  }

  function formatDate(isoDate) {
    try {
      return new Intl.DateTimeFormat("ne-NP", {
        year: "numeric",
        month: "short",
        day: "numeric",
      }).format(new Date(isoDate));
    } catch (err) {
      return isoDate;
    }
  }

  function buildRoadmapItem(item) {
    const meta = STATUS_META[item.status] || STATUS_META.planned;

    const li = document.createElement("li");
    li.className = "jn-roadmap-item";
    li.setAttribute("data-status", item.status);

    li.innerHTML = `
      <span class="jn-roadmap-node ${meta.badgeClass}" aria-hidden="true"></span>
      <div class="jn-roadmap-card">
        <span class="jn-badge-status ${meta.badgeClass}">${meta.label}</span>
        <h3>${jnEscapeHtml(item.title)}</h3>
        <p>${jnEscapeHtml(item.description)}</p>
        <p class="jn-roadmap-meta">
          <span><strong>श्रेणी:</strong> ${jnEscapeHtml(item.category)}</span>
          <span><strong>अपडेट:</strong> <time datetime="${item.updated}">${formatDate(item.updated)}</time></span>
        </p>
      </div>
    `;
    return li;
  }

  async function renderRoadmap() {
    const list = document.getElementById("jn-roadmap-list");
    const status = document.getElementById("jn-roadmap-status");
    if (!list) return;

    try {
      const items = await FETCH_ROADMAP_DATA();

      list.innerHTML = "";

      if (!items || items.length === 0) {
        const empty = document.createElement("li");
        empty.className = "jn-roadmap-empty";
        empty.textContent = "हाल कुनै योजनाबद्ध सुविधा उपलब्ध छैन।";
        list.appendChild(empty);
        if (status) status.textContent = "कुनै रोडम्याप वस्तु फेला परेन।";
        return;
      }

      const fragment = document.createDocumentFragment();
      items.forEach((item) => fragment.appendChild(buildRoadmapItem(item)));
      list.appendChild(fragment);

      if (status) {
        status.textContent = `${items.length} वटा रोडम्याप वस्तुहरू लोड भयो।`;
      }
    } catch (err) {
      list.innerHTML = "";
      const errorItem = document.createElement("li");
      errorItem.className = "jn-roadmap-empty";
      errorItem.textContent =
        "रोडम्याप डाटा लोड गर्न सकिएन। कृपया पछि फेरि प्रयास गर्नुहोस्।";
      list.appendChild(errorItem);
      if (status) status.textContent = "रोडम्याप लोड गर्दा त्रुटि भयो।";
    }
  }

  document.addEventListener("DOMContentLoaded", renderRoadmap);
})();
