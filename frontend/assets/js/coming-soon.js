/**
 * jn-coming-soon.js
 * ---------------------------------------------------------------
 * coming-soon.html ("शीघ्र आउँदैछ!" — Project Roadmap) पेजको
 * पूर्ण रोडम्याप बोर्ड। डेटा /api/roadmap/ बाट आउँछ — यसले छुट्टै
 * Roadmap डाटाबेसको सट्टा प्रत्यक्ष Projects डाटाबेस (योजनामा/
 * विकासमा/परीक्षणमा रहेका मात्र) प्रयोग गर्छ।
 *
 * Accessibility/UX ढाँचा: हरेक कार्डमा अवस्था (status) र प्राथमिकता
 * (priority) सधैँ देखिन्छ — यो "थप हेर्नुहोस्" भन्दा पहिले नै छर्लङ्ग
 * देखिनुपर्छ। बाँकी पूर्ण विवरण (विवरण, प्रगति पट्टी, माइलस्टोन,
 * ट्याग, Download/Visit बटन) native <details>/<summary> (थप
 * हेर्नुहोस्) भित्र लुकेको हुन्छ — स्क्रिन रिडरका लागि यो native
 * HTML ढाँचा नै सबभन्दा पहुँचयोग्य हो।
 *
 * नोट: गृहपृष्ठको सानो रोडम्याप विजेटले अझै assets/js/roadmap.js
 * नै प्रयोग गर्छ — त्यो छुट्टै, सरल संस्करण हो (कार्ड मात्र)।
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

  const PRIORITY_META = {
    low: { label: "न्यून", cssClass: "jn-priority-low" },
    medium: { label: "मध्यम", cssClass: "jn-priority-medium" },
    high: { label: "उच्च", cssClass: "jn-priority-high" },
    critical: { label: "अत्यावश्यक", cssClass: "jn-priority-critical" },
  };

  const ACTION_ICON = { download: "⬇", visit: "🔗" };

  async function fetchRoadmapData() {
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

  function buildMilestonesHtml(milestones) {
    if (!milestones || milestones.length === 0) return "";
    const items = milestones
      .map(
        (m) =>
          `<li data-status="${jnEscapeHtml(m.status)}">${jnEscapeHtml(m.title)} — ${jnEscapeHtml(m.status_label)}</li>`
      )
      .join("");
    return `
      <h4 class="jn-roadmap-subheading">माइलस्टोनहरू (${milestones.length})</h4>
      <ul class="jn-roadmap-milestones">${items}</ul>
    `;
  }

  function buildKeyFeaturesHtml(features) {
    if (!features || features.length === 0) return "";
    const items = features.map((f) => `<li>${jnEscapeHtml(f)}</li>`).join("");
    return `
      <h4 class="jn-roadmap-subheading">मुख्य विशेषताहरू</h4>
      <ul class="jn-project-feature-list">${items}</ul>
    `;
  }

  function buildTargetReleaseHtml(targetRelease) {
    if (!targetRelease || (!targetRelease.version && !targetRelease.date)) return "";
    const parts = [];
    if (targetRelease.version) parts.push(jnEscapeHtml(targetRelease.version));
    if (targetRelease.date) parts.push(`लक्षित मिति: ${formatDate(targetRelease.date)}`);
    return `<p class="jn-roadmap-target-release">🎯 ${parts.join(" · ")}</p>`;
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

  function buildRoadmapItem(item) {
    const statusMeta = STATUS_META[item.status] || STATUS_META.planned;
    const priorityMeta = PRIORITY_META[item.priority] || PRIORITY_META.medium;
    const progress = Math.max(0, Math.min(100, Number(item.progress) || 0));

    const tagsHtml = (item.tags || [])
      .map((t) => `<li>${jnEscapeHtml(t)}</li>`)
      .join("");

    const introHtml = item.introduction
      ? `<p>${jnEscapeHtml(item.introduction)}</p>`
      : `<p>${jnEscapeHtml(item.description)}</p>`;
    const objectiveHtml = item.objective
      ? `<h4 class="jn-roadmap-subheading">उद्देश्य</h4><p>${jnEscapeHtml(item.objective)}</p>`
      : "";
    const audienceHtml = item.target_audience
      ? `<p class="jn-roadmap-audience"><strong>लक्षित समूह:</strong> ${jnEscapeHtml(item.target_audience)}</p>`
      : "";

    const li = document.createElement("li");
    li.className = "jn-roadmap-item";
    li.setAttribute("data-status", item.status);

    li.innerHTML = `
      <span class="jn-roadmap-node ${statusMeta.badgeClass}" aria-hidden="true"></span>
      <div class="jn-roadmap-card">
        <div class="jn-project-card-meta">
          <span class="jn-badge-status ${statusMeta.badgeClass}">${statusMeta.label}</span>
          <span class="jn-priority-badge ${priorityMeta.cssClass}">प्राथमिकता: ${priorityMeta.label}</span>
        </div>
        <h3>${jnEscapeHtml(item.title)}</h3>

        <div class="jn-progress-wrap">
          <div class="jn-progress-label">
            <span>प्रगति</span>
            <span>${progress}%</span>
          </div>
          <div class="jn-progress-track" role="progressbar" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100">
            <div class="jn-progress-fill" style="width: ${progress}%"></div>
          </div>
        </div>

        <details>
          <summary>थप हेर्नुहोस् (पूरा विवरण)</summary>
          <div class="jn-roadmap-details-body">
            ${introHtml}
            ${objectiveHtml}
            ${audienceHtml}
            ${buildKeyFeaturesHtml(item.key_features)}
            ${tagsHtml ? `<ul class="jn-project-tags">${tagsHtml}</ul>` : ""}
            ${buildMilestonesHtml(item.milestones)}
            ${buildTargetReleaseHtml(item.target_release)}
            ${buildActionHtml(item.action)}
            <p class="jn-roadmap-meta">
              <span><strong>श्रेणी:</strong> ${jnEscapeHtml(item.category)}</span>
              <span><strong>अपडेट:</strong> <time datetime="${item.updated}">${formatDate(item.updated)}</time></span>
            </p>
          </div>
        </details>
      </div>
    `;
    return li;
  }

  async function renderRoadmap() {
    const list = document.getElementById("jn-roadmap-list");
    const status = document.getElementById("jn-roadmap-status");
    if (!list) return;

    try {
      const items = await fetchRoadmapData();

      list.innerHTML = "";

      if (!items || items.length === 0) {
        const empty = document.createElement("li");
        empty.className = "jn-roadmap-empty";
        empty.textContent = "हाल कुनै योजनाबद्ध/विकासरत परियोजना उपलब्ध छैन।";
        list.appendChild(empty);
        if (status) status.textContent = "कुनै रोडम्याप वस्तु फेला परेन।";
        return;
      }

      const fragment = document.createDocumentFragment();
      items.forEach((item) => fragment.appendChild(buildRoadmapItem(item)));
      list.appendChild(fragment);

      if (status) {
        status.textContent = `${items.length} वटा परियोजना रोडम्यापमा देखाइँदैछ।`;
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
