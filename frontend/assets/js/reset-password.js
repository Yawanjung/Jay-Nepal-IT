/**
 * jn-reset-password.js
 * ---------------------------------------------------------------
 * reset-password.html — URL बाट ?token=... पढेर, नयाँ पासवर्ड लिएर
 * /api/accounts/reset-password/ लाई पठाउने।
 *
 * सुरक्षा नोट: URL बाट आएको token लाई कहिल्यै raw HTML मा नराखी,
 * सिधै fetch body मा मात्र पठाइन्छ। Token खाली/नभेटिए फारम नै
 * लुकाएर "अमान्य लिङ्क" सन्देश देखाइन्छ।
 * ---------------------------------------------------------------
 */
(function () {
  "use strict";

  function getTokenFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return (params.get("token") || "").trim();
  }

  document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("jn-reset-form");
    if (!form) return;

    const invalidTokenBox = document.getElementById("jn-reset-invalid-token");
    const token = getTokenFromUrl();

    if (!token) {
      form.hidden = true;
      if (invalidTokenBox) invalidTokenBox.hidden = false;
      return;
    }

    const password = document.getElementById("jn-reset-password");
    const passwordFeedback = document.getElementById("jn-reset-password-feedback");
    const passwordConfirm = document.getElementById("jn-reset-password-confirm");
    const passwordConfirmFeedback = document.getElementById("jn-reset-password-confirm-feedback");
    const status = document.getElementById("jn-reset-status");
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      password.classList.remove("is-invalid");
      passwordConfirm.classList.remove("is-invalid");
      if (status) {
        status.dataset.state = "";
        status.textContent = "";
      }

      if (password.value.length < 8) {
        password.classList.add("is-invalid");
        if (passwordFeedback) passwordFeedback.textContent = "पासवर्ड कम्तीमा ८ अक्षरको हुनुपर्छ।";
        password.focus();
        return;
      }

      if (password.value !== passwordConfirm.value) {
        passwordConfirm.classList.add("is-invalid");
        if (passwordConfirmFeedback) passwordConfirmFeedback.textContent = "दुवै पासवर्ड मिलेन।";
        passwordConfirm.focus();
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "बदलिँदैछ…";
      }

      try {
        const response = await jnApiFetch("/accounts/reset-password/", {
          method: "POST",
          body: JSON.stringify({ token: token, password: password.value }),
        });
        const result = await response.json().catch(() => ({}));

        if (response.ok && result.ok) {
          if (status) {
            status.dataset.state = "success";
            status.textContent = result.message || "पासवर्ड सफलतापूर्वक बदलियो। अब लगइन गर्नुहोस्।";
          }
          form.reset();
          setTimeout(function () {
            window.location.href = "login.html";
          }, 2000);
        } else {
          if (status) {
            status.dataset.state = "error";
            status.textContent =
              result.error || "पासवर्ड बदल्न सकिएन। लिङ्कको म्याद सकिएको हुन सक्छ।";
          }
        }
      } catch (err) {
        if (status) {
          status.dataset.state = "error";
          status.textContent = "सर्भरसँग जोडिन सकिएन। इन्टरनेट/सर्भर जाँच गरेर फेरि प्रयास गर्नुहोस्।";
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "पासवर्ड बदल्नुहोस्";
        }
      }
    });
  });
})();
