var language = "";

function handleLanguageChange() {
  window.location.href = `/?target_language=${document.getElementById("language-select").value}`;
}

async function handleSaveClick() {
  try {
    const response = await fetch("/_/save", { method: "POST" });
    if (response.ok) {
      const data = await response.json();
      if (data?.ok !== true) {
        throw new Error(`Error: ${data?.message}`);
      }
      // Good
      showSuccessAlert("Save succeed");
    } else {
      throw new Error(`Http Error #${response.status}: ${response.statusText}`);
    }
  } catch (e) {
    showErrorModal(`${e}`, "Save failed");
  }
}

async function handleSaveAndBuildClick() {
  try {
    const response = await fetch("/_/save_and_build", { method: "POST" });
    if (response.ok) {
      const data = await response.json();
      if (data?.ok !== true) {
        throw new Error(`Error: ${data?.message}`);
      }
      // Good
      showSuccessAlert("Save and build succeed");
    } else {
      throw new Error(`Http Error #${response.status}: ${response.statusText}`);
    }
  } catch (e) {
    showErrorModal(`${e}`, "Save and build failed");
  }
}

async function handleKeyChange(e) {
  // Switch active state
  document.querySelectorAll(".translation-key-item.active").forEach(element => element.classList.remove("active"));
  e.target.classList.add("active");
  // Fetch data and update translation content
  const key = e.target.dataset.value;
  if (key) {
    try {
      const response = await fetch(`/_/translation?key=${encodeURIComponent(key)}&language=${encodeURIComponent(language)}`);
      if (response.ok) {
        const data = await response.json();
        if (data?.ok !== true) {
          throw new Error(`Error: ${data?.message}`);
        }
        updateTranslationContent(data.data);
      } else {
        throw new Error(`Http Error #${response.status}: ${response.statusText}`);
      }
    } catch (e) {
      showErrorModal(`${e}`, "Get translation data failed");
      updateTranslationContent();
    }
  } else {
    updateTranslationContent();
  }
}

function updateTranslationContent(data) {
  // Original
  document.getElementById("translation-original-key").innerHTML = data?.source?.key ?? "";
  document.getElementById("translation-new-key").value = data?.source?.key ?? "";
  document.getElementById("translation-original-values").innerHTML = data?.source?.values?.length > 0
    ? data.source.values.map(value => `<li class="list-group-item">${value?.language}: ${value?.value}</li>`).join("\n")
    : "";
  // Translation
  document.getElementById("translation-new-update-time").innerHTML = `Update time: ${data?.translation?.update_time ?? 'Never'}`;
  document.getElementById("translation-new-value").value = data?.translation?.value ?? "";
  if (data?.source?.key && data?.source?.values?.length > 0) {
    // Enable
    document.getElementById("translation-new-value").removeAttribute("disabled");
    document.getElementById("translation-submit").removeAttribute("disabled");
  } else {
    // Disable
    document.getElementById("translation-new-value").setAttribute("disabled", "");
    document.getElementById("translation-submit").setAttribute("disabled", "");
  }
}

async function submitNewTranslation(e) {
  e.preventDefault();

  // Post data
  const key = document.getElementById("translation-new-key").value;
  const value = document.getElementById("translation-new-value").value;
  if (!key) {
    showErrorModal("Require key");
    return;
  }
  try {
    const response = await fetch("/_/translation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        key,
        value,
        language,
      }),
    });
    if (response.ok) {
      const data = await response.json();
      if (data?.ok !== true) {
        throw new Error(`Error: ${data?.message}`);
      }
      showSuccessAlert("Submit new translation succeed");
    } else {
      throw new Error(`Http Error #${response.status}: ${response.statusText}`);
    }
  } catch (e) {
    showErrorModal(`${e}`, "Submit new translation failed");
  }
}

// Modal utility
var errorModal = null;
var infoModal = null;

function showErrorModal(content, title = 'Error') {
  document.getElementById("modal-error-title").innerHTML = title ?? "";
  document.getElementById("modal-error-body").innerHTML = content ?? "";
  errorModal.show();
}

function showInfoModal(content, title = 'Info') {
  document.getElementById("modal-info-title").innerHTML = title ?? "";
  document.getElementById("modal-info-body").innerHTML = content ?? "";
  infoModal.show();
}

// Alert utility
var successAlertContainer = null;
var successAlertAutoCloseHandler = null;

function showSuccessAlert(message) {
  // Update message
  successAlertContainer.innerHTML = `<div class="alert alert-success" role="alert">${message}</div>`;
  // Auto close
  if (successAlertAutoCloseHandler) {
    clearTimeout(successAlertAutoCloseHandler);
  }
  successAlertAutoCloseHandler = setTimeout(() => successAlertContainer.innerHTML = "", 1500);
}

// On loaded
document.addEventListener('DOMContentLoaded', function () {
  // Initalize values
  language = document.getElementById("language-select").value;
  errorModal = new bootstrap.Modal(document.getElementById("modal-error"), {});
  infoModal = new bootstrap.Modal(document.getElementById("modal-info"), {});
  successAlertContainer = document.getElementById("alert-success-container");

  // Hook events
  document.getElementById("language-select").addEventListener("change", handleLanguageChange);
  document.getElementById("btn-save").addEventListener("click", handleSaveClick);
  document.getElementById("btn-save-and-build").addEventListener("click", handleSaveAndBuildClick);
  document.querySelectorAll(".translation-key-item").forEach(element => element.addEventListener("click", handleKeyChange));
  document.getElementById("translation-submit").addEventListener("click", submitNewTranslation);
});

