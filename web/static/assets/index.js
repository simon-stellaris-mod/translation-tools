var language = "";

const handleInputSearchKeyKeyUp = _.debounce(async e => await updateTranslationKeys(e.target.value ?? ""), 500);

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

async function updateTranslationKeys(query) {
  try {
    const response = await fetch(`/_/keys?language=${language}&query=${query}`);
    if (response.ok) {
      const data = await response.json();
      if (data?.ok !== true) {
        throw new Error(`Error: ${data?.message}`);
      }
      // Good, update key tab
      const updateKeyTab = (keys, sizeElementName, listElementName) => {
        if (keys?.length > 0) {
          const items = [];
          for (const key of keys) {
            items.push(`<li class="list-group-item list-group-item-action translation-key-item" data-value="${key}" onclick="handleTranslationKeyItemClick(event)">${key}</li>`);
          }
          document.getElementById(listElementName).innerHTML = items.join("\n");
          document.getElementById(sizeElementName).innerHTML = `${keys.length}`;
        } else {
          document.getElementById(listElementName).innerHTML = "";
          document.getElementById(sizeElementName).innerHTML = "0";
        }
      }
      updateKeyTab(data?.data?.new_keys, "translation-keys-tab-header-new-key-size", "translation-keys-new-key-list");
      updateKeyTab(data?.data?.changed_keys, "translation-keys-tab-header-changed-key-size", "translation-keys-changed-key-list");
      updateKeyTab(data?.data?.done_keys, "translation-keys-tab-header-done-key-size", "translation-keys-done-key-list");
      updateKeyTab(data?.data?.skipped_keys, "translation-keys-tab-header-skipped-key-size", "translation-keys-skipped-key-list");
    } else {
      throw new Error(`Http Error #${response.status}: ${response.statusText}`);
    }
  } catch (e) {
    showErrorModal(`${e}`, "Update keys failed");
  }
}

async function handleTranslationKeyItemClick(e) {
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
  document.getElementById("translation-original-values").innerHTML = data?.source?.values?.length > 0
    ? data.source.values.map(value =>
      `<li class="list-group-item"><span class="badge text-bg-info prefix-badge">${value?.language}</span>${value?.value ? value.value.replace("\n", "<br>") : ""}</li>`
    ).join("\n")
    : "";
  // Translation
  document.getElementById("translation-translate-key").value = data?.source?.key ?? "";
  document.getElementById("input-translation-translate-value").value = data?.translation?.value ?? "";
  if (data?.translation?.skipped === true) {
    document.getElementById("checkbox-translation-translate-skipped").checked = true;
  } else {
    document.getElementById("checkbox-translation-translate-skipped").checked = false;
  }
  document.getElementById("translation-translate-update-time").innerHTML = `Update time: ${data?.translation?.update_time ?? 'Never'}`;
  if (data?.source?.key && data?.source?.values?.length > 0) {
    // Enable
    document.getElementById("input-translation-translate-value").disabled = false;
    document.getElementById("checkbox-translation-translate-skipped").disabled = false;
    document.getElementById("btn-translation-submit").disabled = false;
  } else {
    // Disable
    document.getElementById("input-translation-translate-value").disabled = true;
    document.getElementById("checkbox-translation-translate-skipped").disabled = true;
    document.getElementById("btn-translation-submit").disabled = true;
  }
}

async function handleSubmitTranslationClick(e) {
  e.preventDefault();

  // Post data
  const key = document.getElementById("translation-translate-key").value;
  const value = document.getElementById("input-translation-translate-value").value;
  const skipped = document.getElementById("checkbox-translation-translate-skipped").checked;
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
        language,
        value,
        skipped,
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

function showErrorModal(content, title = "Error") {
  document.getElementById("modal-error-title").innerHTML = title ?? "";
  document.getElementById("modal-error-body").innerHTML = content ?? "";
  errorModal.show();
}

function showInfoModal(content, title = "Info") {
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

var tooltipList = null;

// On loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initalize values
  language = document.getElementById("language-select").value;
  errorModal = new bootstrap.Modal(document.getElementById("modal-error"), {});
  infoModal = new bootstrap.Modal(document.getElementById("modal-info"), {});
  successAlertContainer = document.getElementById("alert-success-container");
  tooltipList = [...document.querySelectorAll("[data-bs-toggle=\"tooltip\"]")]
    .map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

  // Hook events
  document.getElementById("language-select").addEventListener("change", () => {
    window.location.href = `/?language=${document.getElementById("language-select").value}`;
  });
  document.getElementById("btn-save").addEventListener("click", handleSaveClick);
  document.getElementById("btn-save-and-build").addEventListener("click", handleSaveAndBuildClick);
  document.getElementById("input-search-key").addEventListener("keyup", handleInputSearchKeyKeyUp);
  document.getElementById("btn-refresh-keys").addEventListener("click", () =>
    updateTranslationKeys(document.getElementById("input-search-key").value));
  document.getElementById("btn-translation-submit").addEventListener("click", handleSubmitTranslationClick);

  // Load keys
  updateTranslationKeys("");
});
