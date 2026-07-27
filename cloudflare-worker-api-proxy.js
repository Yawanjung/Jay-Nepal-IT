/**
 * cloudflare-worker-api-proxy.js
 * ---------------------------------------------------------------
 * यो फाइल Django/frontend codebase को हिस्सा होइन — यो केवल
 * Cloudflare Worker मा copy-paste गर्नका लागि हो।
 *
 * उद्देश्य: api.jaynepalit.com मा आउने हरेक request लाई त्यही
 * बाटो/query/header/body सहित सिधै Railway backend
 * (jay-nepal-it-production.up.railway.app) मा पठाउने — user लाई
 * यो happening कहिल्यै थाहा नै हुँदैन, URL मा सधैँ
 * api.jaynepalit.com नै देखिन्छ।
 *
 * किन चाहियो: jaynepalit.com (frontend) र railway.app (backend)
 * पूर्ण फरक domain भएकोले, browser ले backend को cookie लाई
 * "third-party" ठानेर block गर्थ्यो (CSRF/login दुवै बिग्रन्थ्यो)।
 * api.jaynepalit.com जय नेपाल आईटी को आफ्नै subdomain भएकोले, यो
 * समस्या पूर्ण रूपमा हराउँछ।
 *
 * Setup: Cloudflare → Workers & Pages → Create Worker → यो कोड
 * paste गर्नुहोस् → Deploy → त्यसपछि Worker settings → Triggers
 * मा "api.jaynepalit.com/*" भन्ने Route थप्नुहोस्।
 * ---------------------------------------------------------------
 */

const RAILWAY_BACKEND_HOST = "jay-nepal-it-production.up.railway.app";

export default {
  async fetch(request) {
    const incomingUrl = new URL(request.url);

    // बाटो/query उस्तै राखेर, hostname मात्र Railway तिर बदल्ने
    const targetUrl = new URL(incomingUrl.pathname + incomingUrl.search, `https://${RAILWAY_BACKEND_HOST}`);

    // Method/headers/body सबै उस्तै राखेर नयाँ request बनाउने
    const proxiedRequest = new Request(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
      redirect: "manual",
    });

    const response = await fetch(proxiedRequest);

    // Railway बाट आएको जवाफ त्यसै फर्काउने (headers/cookies सहित)
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  },
};
