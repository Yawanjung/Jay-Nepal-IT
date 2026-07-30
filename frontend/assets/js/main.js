/**
 * jn-main.js
 * ---------------------------------------------------------------
 * साइटव्यापी क्लाइन्ट-साइड लजिक: सदस्यता फारम भ्यालिडेशन र
 * स्क्रिन-रिडर-अनुकूल स्थिति सन्देशहरू (aria-live)।
 * ---------------------------------------------------------------
 */
(function () {
  "use strict";

  const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function setInvalid(input, feedbackEl, message) {
    input.setAttribute("aria-invalid", "true");
    input.classList.add("is-invalid");
    if (feedbackEl) feedbackEl.textContent = message;
  }

  function clearInvalid(input, feedbackEl) {
    input.removeAttribute("aria-invalid");
    input.classList.remove("is-invalid");
    if (feedbackEl) feedbackEl.textContent = "";
  }

  function initSubscribeForm() {
    const form = document.getElementById("jn-subscribe-form");
    if (!form) return;

    const emailInput = document.getElementById("jn-subscribe-email");
    const feedback = document.getElementById("jn-subscribe-email-feedback");
    const statusRegion = document.getElementById("jn-subscribe-status");
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener("submit", async function (event) {
      event.preventDefault();

      const rawValue = emailInput.value.trim();
      const tempDiv = document.createElement('div');
      tempDiv.textContent = rawValue;
      const sanitizedValue = tempDiv.innerHTML;

      if (!sanitizedValue) {
        setInvalid(emailInput, feedback, "कृपया आफ्नो इमेल ठेगाना लेख्नुहोस्।");
        emailInput.focus();
        if (statusRegion) {
          statusRegion.dataset.state = "error";
          statusRegion.textContent = "फारम पेश गर्न सकिएन: इमेल आवश्यक छ।";
        }
        return;
      }

      if (!EMAIL_PATTERN.test(sanitizedValue)) {
        setInvalid(
          emailInput,
          feedback,
          "कृपया मान्य इमेल ठेगाना लेख्नुहोस् (जस्तै: example@mail.com)।"
        );
        emailInput.focus();
        if (statusRegion) {
          statusRegion.dataset.state = "error";
          statusRegion.textContent = "फारम पेश गर्न सकिएन: इमेल ढाँचा मिलेन।";
        }
        return;
      }

      clearInvalid(emailInput, feedback);
      if (submitBtn) submitBtn.disabled = true;

      try {
        const response = await jnApiFetch("/news/subscribe/", {
          method: "POST",
          body: JSON.stringify({ email: sanitizedValue }),
        });
        const result = await response.json().catch(() => ({}));

        if (!response.ok || !result.ok) {
          if (statusRegion) {
            statusRegion.dataset.state = "error";
            statusRegion.textContent =
              result.error || "सदस्यता लिन सकिएन। कृपया पछि प्रयास गर्नुहोस्।";
          }
          return;
        }

        form.reset();
        if (statusRegion) {
          statusRegion.dataset.state = "success";
          statusRegion.textContent =
            "धन्यवाद! तपाईंलाई अपडेटहरू इमेल मार्फत पठाइनेछ।";
        }
      } catch (err) {
        if (statusRegion) {
          statusRegion.dataset.state = "error";
          statusRegion.textContent =
            "सर्भरसँग जोडिन सकिएन। इन्टरनेट/सर्भर जाँच गरेर फेरि प्रयास गर्नुहोस्।";
        }
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });

    emailInput.addEventListener("input", function () {
      if (emailInput.classList.contains("is-invalid")) {
        clearInvalid(emailInput, feedback);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initSubscribeForm();
    initPasswordToggles();
    initLoginForm();
    initSignupForm();
    initNavAuthState();
  });

  /* =========================================================
     Navigation bar — Login गरिसकेपछि "लगइन / साइनअप" बटनलाई
     "लगआउट" मा बदल्ने। कुनै HTML फाइल छुनु नपरोस् भनेर, यहाँ
     JS ले नै existing लगइन link (href="login.html") पत्ता
     लगाएर आफैं बदल्छ — सबै पेजमा main.js लोड भइसकेकोले, यो
     एउटै ठाउँबाट सबैतिर लागू हुन्छ।
     ========================================================= */
  async function initNavAuthState() {
    const loginLinks = document.querySelectorAll('a[href="login.html"]');
    if (loginLinks.length === 0) return;

    try {
      const response = await jnApiFetch("/accounts/me/");
      if (!response.ok) return; // लगइन नभएको अवस्था — बटन जस्ताको त्यस्तै रहन्छ

      const data = await response.json();
      const user = data.user || {};
      const displayName = user.first_name || user.username || "प्रयोगकर्ता";

      loginLinks.forEach(function (link) {
        link.textContent = `लगआउट (${displayName})`;
        link.setAttribute("href", "#");
        link.setAttribute("role", "button");
        link.addEventListener("click", async function (event) {
          event.preventDefault();
          try {
            await jnApiFetch("/accounts/logout/", { method: "POST" });
          } catch (err) {
            // silent — logout API नपुगे पनि प्रयोगकर्तालाई homepage मा लैजाने
          }
          window.location.href = "index.html";
        });
      });
    } catch (err) {
      // API नपुगे पनि silently बेवास्ता — बटन जस्ताको त्यस्तै रहन्छ
    }
  }

  /* =========================================================
     पासवर्ड आँखा टगल (Password visibility toggle)
     ========================================================= */
  function initPasswordToggles() {
    const toggles = document.querySelectorAll(".jn-password-toggle");
    toggles.forEach(function (btn) {
      btn.addEventListener("click", function () {
        const targetId = btn.getAttribute("data-target");
        const input = document.getElementById(targetId);
        if (!input) return;

        const isHidden = input.getAttribute("type") === "password";
        input.setAttribute("type", isHidden ? "text" : "password");
        btn.setAttribute("aria-pressed", isHidden ? "true" : "false");
        btn.textContent = isHidden ? "लुकाउनुहोस्" : "देखाउनुहोस्";
        btn.setAttribute(
          "aria-label",
          isHidden ? "पासवर्ड लुकाउनुहोस्" : "पासवर्ड देखाउनुहोस्"
        );
      });
    });
  }

  /* =========================================================
     लगइन फारम भ्यालिडेशन
     ========================================================= */
  function initLoginForm() {
    const form = document.getElementById("jn-login-form");
    if (!form) return;

    const identifier = document.getElementById("jn-login-identifier");
    const identifierFeedback = document.getElementById("jn-login-identifier-feedback");
    const password = document.getElementById("jn-login-password");
    const passwordFeedback = document.getElementById("jn-login-password-feedback");
    const status = document.getElementById("jn-login-status");

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      let hasError = false;

      if (!identifier.value.trim()) {
        setInvalid(identifier, identifierFeedback, "कृपया इमेल वा युजरनेम लेख्नुहोस्।");
        hasError = true;
      } else {
        clearInvalid(identifier, identifierFeedback);
      }

      if (!password.value) {
        setInvalid(password, passwordFeedback, "कृपया पासवर्ड लेख्नुहोस्।");
        hasError = true;
      } else {
        clearInvalid(password, passwordFeedback);
      }

      if (hasError) {
        if (status) {
          status.dataset.state = "error";
          status.textContent = "फारम पेश गर्न सकिएन: माथिका त्रुटिहरू सच्याउनुहोस्।";
        }
        (identifier.classList.contains("is-invalid") ? identifier : password).focus();
        return;
      }

      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      try {
        const response = await jnApiFetch("/accounts/login/", {
          method: "POST",
          body: JSON.stringify({
            identifier: identifier.value.trim(),
            password: password.value,
          }),
        });
        const result = await response.json().catch(() => ({}));

        if (!response.ok || !result.ok) {
          if (status) {
            status.dataset.state = "error";
            status.textContent = result.error || "लगइन असफल भयो। कृपया फेरि प्रयास गर्नुहोस्।";
          }
          return;
        }

        if (status) {
          status.dataset.state = "success";
          status.textContent = `स्वागत छ, ${result.user.username}! गृहपृष्ठमा लैजाँदैछौं…`;
        }
        setTimeout(function () {
          window.location.href = "index.html";
        }, 1000);
      } catch (err) {
        if (status) {
          status.dataset.state = "error";
          status.textContent =
            "सर्भरसँग जोडिन सकिएन। Django backend चलिरहेको छ कि छैन जाँच्नुहोस्।";
        }
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  /* =========================================================
     साइनअप फारम भ्यालिडेशन
     ========================================================= */
  function initSignupForm() {
    const form = document.getElementById("jn-signup-form");
    if (!form) return;

    const name = document.getElementById("jn-signup-name");
    const nameFeedback = document.getElementById("jn-signup-name-feedback");
    const email = document.getElementById("jn-signup-email");
    const emailFeedback = document.getElementById("jn-signup-email-feedback");
    const password = document.getElementById("jn-signup-password");
    const passwordFeedback = document.getElementById("jn-signup-password-feedback");
    const confirm = document.getElementById("jn-signup-confirm");
    const confirmFeedback = document.getElementById("jn-signup-confirm-feedback");
    const status = document.getElementById("jn-signup-status");

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      let hasError = false;

      if (!name.value.trim()) {
        setInvalid(name, nameFeedback, "कृपया आफ्नो पूरा नाम लेख्नुहोस्।");
        hasError = true;
      } else {
        clearInvalid(name, nameFeedback);
      }

      if (!EMAIL_PATTERN.test(email.value.trim())) {
        setInvalid(email, emailFeedback, "कृपया मान्य इमेल ठेगाना लेख्नुहोस्।");
        hasError = true;
      } else {
        clearInvalid(email, emailFeedback);
      }

      if (password.value.length < 8) {
        setInvalid(password, passwordFeedback, "पासवर्ड कम्तीमा ८ अक्षरको हुनुपर्छ।");
        hasError = true;
      } else {
        clearInvalid(password, passwordFeedback);
      }

      if (!confirm.value || confirm.value !== password.value) {
        setInvalid(confirm, confirmFeedback, "पासवर्ड मिलेन। फेरि जाँच्नुहोस्।");
        hasError = true;
      } else {
        clearInvalid(confirm, confirmFeedback);
      }

      if (hasError) {
        if (status) {
          status.dataset.state = "error";
          status.textContent = "फारम पेश गर्न सकिएन: माथिका त्रुटिहरू सच्याउनुहोस्।";
        }
        const firstInvalid = form.querySelector(".is-invalid");
        if (firstInvalid) firstInvalid.focus();
        return;
      }

      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      try {
        const response = await jnApiFetch("/accounts/signup/", {
          method: "POST",
          body: JSON.stringify({
            fullname: name.value.trim(),
            email: email.value.trim(),
            password: password.value,
          }),
        });
        const result = await response.json().catch(() => ({}));

        if (!response.ok || !result.ok) {
          if (status) {
            status.dataset.state = "error";
            status.textContent = result.error || "खाता बनाउन सकिएन। कृपया फेरि प्रयास गर्नुहोस्।";
          }
          return;
        }

        form.reset();
        if (status) {
          status.dataset.state = "success";
          status.textContent = "खाता सफलतापूर्वक बन्यो! अब माथिबाट लगइन गर्नुहोस्।";
        }
      } catch (err) {
        if (status) {
          status.dataset.state = "error";
          status.textContent =
            "सर्भरसँग जोडिन सकिएन। Django backend चलिरहेको छ कि छैन जाँच्नुहोस्।";
        }
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }
})();