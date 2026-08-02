/**
 * jn-forgot-password.js
 * ---------------------------------------------------------------
 * forgot-password.html — इमेल लिएर /api/accounts/forgot-password/
 * लाई पठाउने। Backend ले सधैँ उस्तै generic सफल सन्देश दिन्छ
 * (खाता भेटियोस् वा नभेटियोस्, user enumeration रोक्न) — त्यसैले
 * यहाँ पनि सधैँ उस्तै सफल सन्देश देखाइन्छ, "खाता भेटिएन" जस्तो
 * होइन।
 * ---------------------------------------------------------------
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("jn-forgot-form");
    if (!form) return;

    const email = document.getElementById("jn-forgot-email");
    const emailFeedback = document.getElementById("jn-forgot-email-feedback");
    const status = document.getElementById("jn-forgot-status");
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      email.classList.remove("is-invalid");
      if (status) {
        status.dataset.state = "";
        status.textContent = "";
      }

      if (!email.value.trim() || !email.checkValidity()) {
        email.classList.add("is-invalid");
        if (emailFeedback) emailFeedback.textContent = "कृपया मान्य इमेल ठेगाना लेख्नुहोस्।";
        email.focus();
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "पठाइँदैछ…";
      }

      try {
        const response = await jnApiFetch("/accounts/forgot-password/", {
          method: "POST",
          body: JSON.stringify({ email: email.value.trim() }),
        });
        const result = await response.json().catch(() => ({}));

        if (status) {
          status.dataset.state = response.ok && result.ok ? "success" : "error";
          status.textContent =
            result.message ||
            result.error ||
            "यदि यो इमेलबाट खाता बनेको छ भने, पासवर्ड रिसेट लिङ्क पठाइयो।";
        }
        if (response.ok && result.ok) {
          form.reset();
        }
      } catch (err) {
        if (status) {
          status.dataset.state = "error";
          status.textContent = "सर्भरसँग जोडिन सकिएन। इन्टरनेट/सर्भर जाँच गरेर फेरि प्रयास गर्नुहोस्।";
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "रिसेट लिङ्क पठाउनुहोस्";
        }
      }
    });
  });
})();
