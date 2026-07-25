/**
 * jn-home.js
 * ---------------------------------------------------------------
 * गृहपृष्ठका दुई "हाइलाइट" खण्ड — प्रमुख परियोजनाहरू र समाचार प्रिभ्यु —
 * लाई static राख्नुको सट्टा /api/projects/featured/ र /api/news/
 * बाट लाइभ डेटा तानेर देखाउँछ, ताकि admin बाट थपेको नयाँ content
 * तुरुन्तै गृहपृष्ठमा पनि झुल्कियोस्।
 * ---------------------------------------------------------------
 */
(function () {
  "use strict";

  const HOME_NEWS_LIMIT = 2;
  const HOME_FEATURES_LIMIT = 2;

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

  /* ===================== प्रमुख परियोजनाहरू ===================== */
  function buildFeatureCard(project) {
    const col = document.createElement("div");
    col.className = "col-12 col-md-4";
    col.innerHTML = `
      <article class="jn-feature-card">
        <div class="jn-feature-icon" aria-hidden="true">${jnEscapeHtml(project.icon_emoji) || "📦"}</div>
        <h3>${jnEscapeHtml(project.title)}</h3>
        <p>${jnEscapeHtml(project.summary)}</p>
        <a href="projects.html#project-${project.id}" class="fw-semibold">
          थप हेर्नुहोस् <span class="visually-hidden">— ${jnEscapeHtml(project.title)} को बारेमा</span>
        </a>
      </article>
    `;
    return col;
  }

  async function loadHomeFeaturedProjects() {
    const grid = document.getElementById("jn-home-features-grid");
    const status = document.getElementById("jn-home-features-status");
    if (!grid) return;

    try {
      const response = await jnApiFetch("/projects/featured/");
      if (!response.ok) throw new Error(`featured projects API त्रुटि: ${response.status}`);
      const data = await response.json();
      const projects = data.results || [];

      grid.innerHTML = "";

      if (projects.length === 0) {
        grid.innerHTML =
          '<div class="col-12"><p class="jn-news-empty">हाल कुनै featured परियोजना छैन। Admin बाट "Is featured" ✓ गरेर थप्नुहोस्।</p></div>';
        if (status) status.textContent = "कुनै featured परियोजना फेला परेन।";
        return;
      }

      const fragment = document.createDocumentFragment();
      projects.slice(0, HOME_FEATURES_LIMIT).forEach((p) => fragment.appendChild(buildFeatureCard(p)));
      grid.appendChild(fragment);

      if (status) status.textContent = `${Math.min(projects.length, HOME_FEATURES_LIMIT)} परियोजना देखाइँदैछ।`;
    } catch (err) {
      grid.innerHTML =
        '<div class="col-12"><p class="jn-news-empty">परियोजना लोड गर्न सकिएन। Backend चलिरहेको छ कि जाँच्नुहोस्।</p></div>';
      if (status) status.textContent = "परियोजना लोड गर्दा त्रुटि भयो।";
    }
  }

  /* ===================== समाचार प्रिभ्यु ===================== */

  /** Body लाई खाली-लाइनका आधारमा अनुच्छेदमा छुट्याएर, हरेक अनुच्छेद
   * escape गरेर मात्र <p> बनाउने — कहिल्यै raw HTML होइन (XSS-सुरक्षित)। */
  function buildBodyHtml(body) {
    const paragraphs = (body || "")
      .split(/\r?\n\s*\r?\n/)
      .map((p) => p.trim())
      .filter(Boolean);

    if (paragraphs.length === 0) return "";

    return paragraphs
      .map((p) => `<p>${jnEscapeHtml(p).replace(/\r?\n/g, "<br />")}</p>`)
      .join("");
  }

  function buildHomeNewsCard(post) {
    const bodyHtml = buildBodyHtml(post.body);
    const col = document.createElement("div");
    col.className = "col-12 col-md-6 col-lg-4";
    col.innerHTML = `
      <article class="jn-news-card">
        <div class="card-body p-4">
          <span class="jn-news-tag">${jnEscapeHtml(post.category_label)}</span>
          <h3>${jnEscapeHtml(post.title)}</h3>
          <p class="mb-2">${jnEscapeHtml(post.excerpt)}</p>

          ${
            bodyHtml
              ? `<details>
                   <summary>थप पढ्नुहोस्</summary>
                   <div class="jn-news-detail-body">${bodyHtml}</div>
                 </details>`
              : ""
          }

          <div class="jn-news-footer">
            <time datetime="${post.published}">${formatDate(post.published)}</time>
            ${post.author_name ? `<span class="jn-news-author">— ${jnEscapeHtml(post.author_name)}</span>` : ""}
          </div>
        </div>
      </article>
    `;
    return col;
  }

  async function loadHomeLatestNews() {
    const grid = document.getElementById("jn-home-news-grid");
    const status = document.getElementById("jn-home-news-status");
    if (!grid) return;

    try {
      const response = await jnApiFetch("/news/");
      if (!response.ok) throw new Error(`news API त्रुटि: ${response.status}`);
      const data = await response.json();
      const posts = (data.results || []).slice(0, HOME_NEWS_LIMIT);

      grid.innerHTML = "";

      if (posts.length === 0) {
        grid.innerHTML = '<div class="col-12"><p class="jn-news-empty">हाल कुनै समाचार छैन।</p></div>';
        if (status) status.textContent = "कुनै समाचार फेला परेन।";
        return;
      }

      const fragment = document.createDocumentFragment();
      posts.forEach((p) => fragment.appendChild(buildHomeNewsCard(p)));
      grid.appendChild(fragment);

      if (status) status.textContent = `${posts.length} समाचार देखाइँदैछ।`;
    } catch (err) {
      grid.innerHTML =
        '<div class="col-12"><p class="jn-news-empty">समाचार लोड गर्न सकिएन। Backend चलिरहेको छ कि जाँच्नुहोस्।</p></div>';
      if (status) status.textContent = "समाचार लोड गर्दा त्रुटि भयो।";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    loadHomeFeaturedProjects();
    loadHomeLatestNews();
  });
})();
