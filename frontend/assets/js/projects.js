/**
 * jn-projects.js
 * ---------------------------------------------------------------
 * projects.html को मुख्य ग्रिड र "हाम्रा मुख्य परियोजनाहरू" साइडबार
 * /api/projects/ र /api/projects/featured/ बाट लाइभ भर्ने।
 *
 * Accessibility/UX ढाँचा: हरेक कार्डमा श्रेणी (category) र अवस्था
 * (status) सधैँ देखिन्छ — यो "थप हेर्नुहोस्" भन्दा पहिले नै छर्लङ्ग
 * देखिनुपर्छ। बाँकी पूर्ण विवरण (परिचय/उद्देश्य/विशेषता/लक्षित समूह,
 * ट्याग, र Download/Visit Live Site बटन) native <details>/<summary>
 * ("थप हेर्नुहोस्") भित्र लुकेको हुन्छ — पूरा भएको/उपलब्ध भएको
 * परियोजनाको हकमा Download/Visit बटन त्यही भित्र मात्र देखिन्छ।
 *
 * नोट: यो पेजले सबै परियोजना (जुनसुकै status) देखाउँछ। Milestones/
 * Progress जस्ता रोडम्याप-सम्बन्धी विवरण भने यहाँ छैनन् — त्यो
 * जानकारी coming-soon.html (शीघ्र आउँदैछ! / Project Roadmap) मा
 * हेर्न सकिन्छ, ताकि दुई पेजबीच डेटा नदोहोरियोस्।
 * ---------------------------------------------------------------
 */
(function () {
  "use strict";

  const CATEGORY_TAG_CLASS = {
    software: "jn-tag-software",
    mobile_app: "jn-tag-mobile",
    web_portal: "jn-tag-webportal",
    game: "jn-tag-game",
  };

  const STATUS_BADGE_CLASS = {
    planned: "jn-badge-planned",
    in_progress: "jn-badge-progress",
    testing: "jn-badge-testing",
    active: "jn-badge-active",
    archived: "jn-badge-archived",
  };

  const ACTION_ICON = { download: "⬇", visit: "🔗" };

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

  function buildKeyFeaturesHtml(features) {
    if (!features || features.length === 0) return "";
    const items = features.map((f) => `<li>${jnEscapeHtml(f)}</li>`).join("");
    return `
      <h4 class="jn-roadmap-subheading">मुख्य विशेषताहरू</h4>
      <ul class="jn-project-feature-list">${items}</ul>
    `;
  }

  function buildActionHtml(action) {
    if (!action || !action.available || !action.url) return "";
    const icon = ACTION_ICON[action.kind] || "⬇";
    return `
      <div class="jn-project-download">
        <a class="btn jn-btn-download" href="${jnSanitizeUrl(action.url)}">
          <span aria-hidden="true">${icon}</span> ${jnEscapeHtml(action.label)}
        </a>
      </div>
    `;
  }

  function buildProjectCard(project) {
    const tagClass = CATEGORY_TAG_CLASS[project.category] || "jn-tag-software";
    const statusClass = STATUS_BADGE_CLASS[project.status] || "jn-badge-planned";

    const tagsHtml = (project.tags || [])
      .map((t) => `<li>${jnEscapeHtml(t)}</li>`)
      .join("");

    const thumbHtml = project.screenshot_url
      ? `<div class="jn-project-thumb">
           <img src="${jnSanitizeUrl(project.screenshot_url)}" alt="" loading="lazy" />
         </div>`
      : "";

    const introHtml = project.introduction
      ? `<p>${jnEscapeHtml(project.introduction)}</p>`
      : project.description
      ? `<p>${jnEscapeHtml(project.description)}</p>`
      : "";
    const objectiveHtml = project.objective
      ? `<h4 class="jn-roadmap-subheading">उद्देश्य</h4><p>${jnEscapeHtml(project.objective)}</p>`
      : "";
    const audienceHtml = project.target_audience
      ? `<p class="jn-roadmap-audience"><strong>लक्षित समूह:</strong> ${jnEscapeHtml(project.target_audience)}</p>`
      : "";

    const wrapper = document.createElement("div");
    wrapper.className = "col-12 col-md-6";
    wrapper.id = `project-${project.id}`;

    wrapper.innerHTML = `
      <article class="jn-project-card">
        ${thumbHtml}
        <div class="jn-project-card-meta">
          <span class="jn-project-tag ${tagClass}">${jnEscapeHtml(project.category_label)}</span>
          <span class="jn-project-status-badge ${statusClass}">${jnEscapeHtml(project.status_label)}</span>
        </div>
        <h3>${project.icon_emoji ? jnEscapeHtml(project.icon_emoji) + " " : ""}${jnEscapeHtml(project.title)}</h3>
        <p>${jnEscapeHtml(project.summary)}</p>

        <details>
          <summary>थप हेर्नुहोस् (पूरा विवरण)</summary>
          <div class="jn-roadmap-details-body">
            ${introHtml}
            ${objectiveHtml}
            ${audienceHtml}
            ${buildKeyFeaturesHtml(project.key_features)}
            ${tagsHtml ? `<ul class="jn-project-tags">${tagsHtml}</ul>` : ""}
            ${buildActionHtml(project.action)}
            <time datetime="${project.updated}">${formatDate(project.updated)} मा अपडेट</time>
          </div>
        </details>
      </article>
    `;
    return wrapper;
  }

  async function loadProjectGrid() {
    const grid = document.getElementById("jn-projects-grid");
    const status = document.getElementById("jn-projects-status");
    if (!grid) return;

    try {
      const response = await jnApiFetch("/projects/");
      if (!response.ok) throw new Error(`projects API त्रुटि: ${response.status}`);
      const data = await response.json();
      const projects = data.results || [];

      grid.innerHTML = "";

      if (projects.length === 0) {
        grid.innerHTML = '<div class="col-12"><p class="jn-news-empty">हाल कुनै परियोजना थपिएको छैन।</p></div>';
        if (status) status.textContent = "कुनै परियोजना फेला परेन।";
        return;
      }

      const fragment = document.createDocumentFragment();
      projects.forEach((p) => fragment.appendChild(buildProjectCard(p)));
      grid.appendChild(fragment);

      if (status) status.textContent = `${projects.length} परियोजना देखाइँदैछ।`;
    } catch (err) {
      grid.innerHTML =
        '<div class="col-12"><p class="jn-news-empty">परियोजना लोड गर्न सकिएन। Backend चलिरहेको छ कि जाँच्नुहोस्।</p></div>';
      if (status) status.textContent = "परियोजना लोड गर्दा त्रुटि भयो।";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    loadProjectGrid();
  });
})();
