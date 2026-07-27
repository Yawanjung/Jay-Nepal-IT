/**
 * jn-api-config.js
 * ---------------------------------------------------------------
 * Django backend सँग जोड्ने साझा सेटिङ र सुरक्षित fetch wrapper।
 *
 * JN_API_BASE अब आफैं पत्ता लगाइन्छ:
 * - localhost/127.0.0.1 (लोकल dev, python -m http.server) मा
 *   चलिरहँदा -> http://127.0.0.1:8000/api
 * - अरू जुनसुकै डोमेन (jaynepalit.com/Firebase Hosting) मा
 *   चलिरहँदा -> https://api.jaynepalit.com/api
 *   (यो Cloudflare Worker मार्फत Railway backend मा proxy हुन्छ —
 *   frontend र backend दुवै अब jaynepalit.com कै subdomain भएकोले
 *   "same-site" मानिन्छन्, third-party cookie block हुँदैन।)
 * ---------------------------------------------------------------
 */
const JN_IS_LOCAL_DEV =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

window.JN_API_BASE =
  window.JN_API_BASE ||
  (JN_IS_LOCAL_DEV ? "http://127.0.0.1:8000/api" : "https://api.jaynepalit.com/api");

function jnGetCookie(name) {
  const match = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
  return match ? decodeURIComponent(match[1]) : null;
}

/** पेज लोड हुनासाथ CSRF कुकी लिन्छ, ताकि पहिलो फारम पेश गर्दा ढिलाइ नहोस्। */
async function jnEnsureCsrfCookie() {
  if (jnGetCookie("csrftoken")) return;
  try {
    await fetch(`${window.JN_API_BASE}/accounts/csrf/`, { credentials: "include" });
  } catch (err) {
    // साइलेन्ट — पहिलो POST प्रयासमा फेरि प्रयास हुनेछ।
  }
}

/**
 * सुरक्षित API कल — GET/POST सबैका लागि प्रयोग गर्नुहोस्।
 * `path` ले app-level prefix सहित पथ लिन्छ, जस्तै: "/roadmap/", "/news/", "/accounts/login/"
 */
async function jnApiFetch(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = new Headers(options.headers || {});

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (method !== "GET" && method !== "HEAD") {
    let token = jnGetCookie("csrftoken");
    if (!token) {
      await jnEnsureCsrfCookie();
      token = jnGetCookie("csrftoken");
    }
    if (token) headers.set("X-CSRFToken", token);
  }

  return fetch(`${window.JN_API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });
}

document.addEventListener("DOMContentLoaded", jnEnsureCsrfCookie);

/**
 * jnEscapeHtml — कुनै पनि टेक्स्ट (Admin बाट आएको title/description/bio आदि)
 * लाई innerHTML भित्र सुरक्षित रूपमा insert गर्नुअघि प्रयोग गर्नुहोस्।
 * यसले <script> जस्ता ट्यागहरूलाई सादा टेक्स्टमा बदलिदिन्छ (Stored XSS रोक्न)।
 */
function jnEscapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/**
 * jnSanitizeUrl — Admin बाट आएको URL (avatar_url, portfolio_url आदि) लाई
 * href/src मा राख्नुअघि प्रयोग गर्नुहोस्। http/https बाहेकका scheme
 * (जस्तै javascript:) लाई ब्लक गर्छ।
 */
function jnSanitizeUrl(url) {
  if (!url) return "";
  try {
    const parsed = new URL(url, window.location.href);
    if (parsed.protocol === "http:" || parsed.protocol === "https:") {
      return parsed.href;
    }
  } catch (err) {
    // अमान्य URL — खाली फर्काउने
  }
  return "";
}
