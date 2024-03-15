<!doctype html>
<html lang="en" data-bs-theme="auto">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Stellaris Translation Tool</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link href="/assets/index.css" rel="stylesheet">

    <script>
        /* Auto switch color mode */
        (
            function () {
                const htmlElement = document.querySelector("html");
                if (htmlElement.getAttribute("data-bs-theme") === "auto") {
                    function updateTheme() {
                        document.querySelector("html").setAttribute("data-bs-theme",
                            window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
                    }
                    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", updateTheme);
                    updateTheme();
                }
            }
        )();
    </script>
</head>

<body>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
        crossorigin="anonymous"></script>
    <script src="/assets/index.js"></script>
    <div class="index-root">
        <div id="alert-success-container">
        </div>
        <nav class="index-navbar navbar bg-body-tertiary">
            <div class="container-fluid">
                <a class="navbar-brand">Stellaris Translation</a>
                <div class="navbar-tools">
                    <button id="btn-save" class="btn btn-primary btn-save" type="button" aria-label="Save">
                        Save (all languages)
                    </button>
                    <button id="btn-save-and-build" class="btn btn-success btn-save-and-build" type="button"
                        aria-label="Save and build">
                        Save and build (all languages)
                    </button>
                    <select id="language-select" class="form-select language-select"
                        aria-label="Select translation target language">
                        % for language in languages:
                        <option value="{{language}}" {{"selected" if language==target_language else "" }}>{{language}}
                        </option>
                        % end
                    </select>
                    </form>
                </div>
        </nav>
        <div class="index-content">
            <div class="translation-keys">
                <div class="translation-keys-inner-container">
                    <!-- New keys -->
                    <div class="card translation-key-card">
                        <div class="card-body">
                            <h5 class="card-title">New keys</h5>
                            <p class="card-text">Keys which doesn't have translation in target language</p>
                        </div>
                        <ul class="list-group list-group-flush ">
                            %for key in new_keys:
                            <li class="list-group-item list-group-item-action translation-key-item"
                                data-value="{{key}}">
                                {{key}}
                                <span class="badge text-bg-primary rounded-pill">New</span>
                            </li>
                            %end
                        </ul>
                    </div>
                    <!-- Changed keys -->
                    <div class="card translation-key-card">
                        <div class="card-body">
                            <h5 class="card-title">Changed keys</h5>
                            <p class="card-text">
                                Keys which have changed its original value after translated in target language
                            </p>
                        </div>
                        <ul class="list-group list-group-flush">
                            %for key in changed_keys:
                            <li class="list-group-item list-group-item-action translation-key-item"
                                data-value="{{key}}">
                                {{key}}
                                <span class="badge text-bg-warning rounded-pill">Changed</span>
                            </li>
                            %end
                        </ul>
                    </div>
                    <!-- Done keys -->
                    <div class="card translation-key-card">
                        <div class="card-body">
                            <h5 class="card-title">Done keys</h5>
                            <p class="card-text">Keys which has translation in target language</p>
                        </div>
                        <ul class="list-group list-group-flush">
                            %for key in done_keys:
                            <li class="list-group-item list-group-item-action translation-key-item"
                                data-value="{{key}}">
                                {{key}}
                                <span class="badge text-bg-success rounded-pill">Done</span>
                            </li>
                            %end
                        </ul>
                    </div>
                </div>
            </div>
            <div class="translation-content">
                <!-- Translation: Original content -->
                <div class="card translation-content-card translation-content-original-value">
                    <div class="card-body">
                        <h5 id="translation-original-key" class="card-title"></h5>
                    </div>
                    <ul id="translation-original-values" class="list-group list-group-flush">
                    </ul>
                </div>
                <!-- Translation: Translated content -->
                <div class="card translation-content-card translation-content-new-value">
                    <div class="card-body">
                        <h5 class="card-title">Translation</h5>
                        <h6 id="translation-new-update-time" class="card-subtitle mb-2 text-body-secondary">Update time:
                            Never</h6>
                        <form id="translation-new-value-form">
                            <input type="hidden" id="translation-new-key">
                            <div class="mb-3">
                                <label for="translation-new-value" class="form-label">Translated value</label>
                                <textarea id="translation-new-value" class="form-control" rows="5" disabled></textarea>
                            </div>
                            <p>Attention: All " and \ will be automatically escaped</p>
                            <button id="translation-submit" type="submit" class="btn btn-primary"
                                disabled>Submit</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Error Modal -->
    <div class="modal fade" id="modal-error" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"
        aria-labelledby="model-error" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="modal-error-title">Error</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="modal-error-body">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal">OK</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Info Modal -->
    <div class="modal fade" id="modal-info" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"
        aria-labelledby="modal-info" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="modal-info-title">Info</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="modal-info-body">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal">OK</button>
                </div>
            </div>
        </div>
    </div>
</body>

</html>
