/**
 * jn-news.js
 * ---------------------------------------------------------------
 * "हाम्रो समाचार" फिड — वर्गीकृत, फिल्टर योग्य, र "थप लोड गर्नुहोस्"
 * सहितको डाइनामिक समाचार सूची। डेटा /api/news/ बाट लाइभ तानिन्छ।
 *
 * "थप पढ्नुहोस्" (Show More): projects.html/coming-soon.html मा
 * प्रयोग गरिएकै inline <details>/<summary> ढाँचा — छुट्टै पेज वा
 * थप fetch बिना, कार्डभित्रै पूरा विवरण (Body, लेखक, मिति) देखिन्छ।
 * Body लाई कहिल्यै raw HTML होइन — खाली-लाइनका आधारमा अनुच्छेद
 * छुट्याएर, हरेक अनुच्छेद escape गरेर मात्र देखाइन्छ (XSS-सुरक्षित)।
 * ---------------------------------------------------------------
 */
(function () {
  "use strict";

  const CATEGORY_META = {
    all: { label: "सबै" },
    special: { label: "विशेष समाचार" },
    milestone: { label: "सफ्टवेयर माइलस्टोन" },
    community: { label: "समुदाय अपडेटहरू" },
  };

  const PAGE_SIZE = 3;
  let currentCategory = "all";
  let visibleCount = PAGE_SIZE;
  let allItems = [];

  async function FETCH_NEWS_DATA() {
    const response = await jnApiFetch("/news/");
    if (!response.ok) {
      throw new Error(`समाचार API त्रुटि: ${response.status}`);
    }
    const data = await response.json();
    // backend ले { category, title, excerpt, body, author_name, version, published } फिल्ड दिन्छ
    return (data.results || []).map((item) => ({
      id: item.slug,
      category: item.category,
      title: item.title,
      excerpt: item.excerpt,
      body: item.body,
      authorName: item.author_name,
      version: item.version,
      published: item.published,
    }));
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

  function buildNewsCard(item) {
    const categoryLabel = CATEGORY_META[item.category]?.label || item.category;
    const bodyHtml = buildBodyHtml(item.body);
    const li = document.createElement("li");
    li.className = "jn-news-full-card";
    li.setAttribute("data-category", item.category);

    li.innerHTML = `
      <span class="jn-news-tag">${jnEscapeHtml(categoryLabel)}</span>
      <h3>${jnEscapeHtml(item.title)}${item.version ? `<span class="jn-news-version">${jnEscapeHtml(item.version)}</span>` : ""}</h3>
      <p>${jnEscapeHtml(item.excerpt)}</p>

      ${
        bodyHtml
          ? `<details>
               <summary>थप पढ्नुहोस्</summary>
               <div class="jn-news-detail-body">${bodyHtml}</div>
             </details>`
          : ""
      }

      <div class="jn-news-footer">
        <time datetime="${item.published}">${formatDate(item.published)}</time>
        ${item.authorName ? `<span class="jn-news-author">— ${jnEscapeHtml(item.authorName)}</span>` : ""}
      </div>
    `;
    return li;
  }

  function renderList() {
    const list = document.getElementById("jn-news-list");
    const status = document.getElementById("jn-news-status");
    const loadMoreWrap = document.getElementById("jn-load-more-wrap");
    if (!list) return;

    const filtered =
      currentCategory === "all"
        ? allItems
        : allItems.filter((item) => item.category === currentCategory);

    list.innerHTML = "";

    if (filtered.length === 0) {
      const empty = document.createElement("li");
      empty.className = "jn-news-empty";
      empty.textContent = "यस श्रेणीमा हाल कुनै समाचार छैन।";
      list.appendChild(empty);
      if (status) status.textContent = "यस श्रेणीमा कुनै समाचार फेला परेन।";
      if (loadMoreWrap) loadMoreWrap.hidden = true;
      return;
    }

    const toShow = filtered.slice(0, visibleCount);
    const fragment = document.createDocumentFragment();
    toShow.forEach((item) => fragment.appendChild(buildNewsCard(item)));
    list.appendChild(fragment);

    if (status) {
      status.textContent = `${toShow.length} मध्ये ${filtered.length} समाचार देखाइँदैछ।`;
    }
    if (loadMoreWrap) {
      loadMoreWrap.hidden = toShow.length >= filtered.length;
    }
  }

  function initFilters() {
    const buttons = document.querySelectorAll(".jn-filter-btn");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.setAttribute("aria-pressed", "false"));
        btn.setAttribute("aria-pressed", "true");
        currentCategory = btn.getAttribute("data-category");
        visibleCount = PAGE_SIZE;
        renderList();
      });
    });
  }

  function initLoadMore() {
    const btn = document.getElementById("jn-load-more-btn");
    if (!btn) return;
    btn.addEventListener("click", () => {
      visibleCount += PAGE_SIZE;
      renderList();
    });
  }

  async function init() {
    const list = document.getElementById("jn-news-list");
    if (!list) return;

    try {
      allItems = await FETCH_NEWS_DATA();
      renderList();
    } catch (err) {
      list.innerHTML = "";
      const errorItem = document.createElement("li");
      errorItem.className = "jn-news-empty";
      errorItem.textContent = "समाचार लोड गर्न सकिएन। कृपया पछि फेरि प्रयास गर्नुहोस्।";
      list.appendChild(errorItem);
    }

    initFilters();
    initLoadMore();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
