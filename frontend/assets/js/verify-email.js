(function () {
  "use strict";

  async function runVerification() {
    const statusBox = document.getElementById("jn-verify-status");
    const resendSection = document.getElementById("jn-verify-resend");
    if (!statusBox) return;

    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (!token) {
      statusBox.dataset.state = "error";
      statusBox.textContent = "प्रमाणीकरण टोकन फेला परेन। कृपया इमेलमा भएको लिङ्क सिधै प्रयोग गर्नुहोस्।";
      return;
    }

    statusBox.dataset.state = "loading";
    statusBox.textContent = "प्रमाणीकरण गर्दैछौं…";

    try {
      const response = await jnApiFetch(`/accounts/verify-email/?token=${encodeURIComponent(token)}`);
      const result = await response.json().catch(() => ({}));

      if (!response.ok || !result.ok) {
        statusBox.dataset.state = "error";
        statusBox.textContent = result.error || "प्रमाणीकरण असफल भयो।";
        if (resendSection) resendSection.hidden = false;
        return;
      }

      statusBox.dataset.state = "success";
      statusBox.textContent = "✅ तपाईंको इमेल सफलतापूर्वक प्रमाणित भयो! अब लगइन गर्न सक्नुहुन्छ।";

      const loginLink = document.getElementById("jn-verify-login-link");
      if (loginLink) loginLink.hidden = false;
    } catch (err) {
      statusBox.dataset.state = "error";
      statusBox.textContent = "सर्भरसँग जोडिन सकिएन। Django backend चलिरहेको छ कि जाँच्नुहोस्।";
      if (resendSection) resendSection.hidden = false;
    }
  }

  function initResendForm() {
    const form = document.getElementById("jn-resend-form");
    if (!form) return;

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      const emailInput = document.getElementById("jn-resend-email");
      const status = document.getElementById("jn-resend-status");
      const submitBtn = form.querySelector('button[type="submit"]');

      if (!emailInput.value.trim()) return;

      if (submitBtn) submitBtn.disabled = true;
      try {
        const response = await jnApiFetch("/accounts/resend-verification/", {
          method: "POST",
          body: JSON.stringify({ email: emailInput.value.trim() }),
        });
        const result = await response.json().catch(() => ({}));
        if (status) {
          status.dataset.state = "success";
          status.textContent = result.message || "यदि खाता अवस्थित छ भने, इमेल पठाइयो।";
        }
      } catch (err) {
        if (status) {
          status.dataset.state = "error";
          status.textContent = "सर्भरसँग जोडिन सकिएन।";
        }
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    runVerification();
    initResendForm();
  });
})();
