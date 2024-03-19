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
    <script src="https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js"></script>
    <script src="/assets/index.js"></script>
    <div class="index-root">
        <div id="alert-success-container">
        </div>
        <nav class="index-navbar navbar bg-body-tertiary">
            <div class="container-fluid">
                <a class="navbar-brand">Stellaris Translation</a>
                <!-- Toolbar -->
                <div class="navbar-tools">
                    <button id="btn-save" class="btn btn-primary btn-save" type="button" aria-label="Save">
                        Save (all languages)
                    </button>
                    <button id="btn-save-and-build" class="btn btn-success btn-save-and-build" type="button"
                        aria-label="Save and build">
                        Save and build (all languages)
                    </button>
                    <select id="language-select" class="form-select language-select"
                        aria-label="Select translation language">
                        % for lang in languages:
                        <option value="{{lang}}" {{"selected" if lang==language else "" }}>{{lang}}
                        </option>
                        % end
                    </select>
                    </form>
                </div>
        </nav>
        <div class="index-content">
            <div class="translation-keys">
                <div class="translation-keys-inner-container">
                    <!-- Search key box -->
                    <div class="translation-keys-search-container input-group mb-3">
                        <span class="input-group-text" id="Search-key">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                class="bi bi-search" viewBox="0 0 16 16">
                                <path
                                    d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0" />
                            </svg>
                        </span>
                        <input id="input-search-key" type="text" class="form-control" placeholder="Search Content"
                            aria-label="Search" aria-describedby="Search-key">
                        <button class="btn btn-outline-secondary" type="button" id="btn-refresh-keys">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                class="bi bi-arrow-clockwise" viewBox="0 0 16 16">
                                <path fill-rule="evenodd"
                                    d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z" />
                                <path
                                    d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466" />
                            </svg>
                        </button>
                    </div>
                    <!-- Keys tab header-->
                    <ul class="nav nav-tabs translation-keys-tab-header" id="myTab" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="new-keys-tab" data-bs-toggle="tab"
                                data-bs-target="#new-keys-tab-pane" type="button" role="tab"
                                aria-controls="new-keys-tab-pane" aria-selected="true">
                                <span data-bs-toggle="tooltip" data-bs-placement="top"
                                    data-bs-title="Keys which doesn't have translation in target language">New</span>
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="changed-keys-tab" data-bs-toggle="tab"
                                data-bs-target="#changed-keys-tab-pane" type="button" role="tab"
                                aria-controls="changed-keys-tab-pane" aria-selected="false">
                                <span data-bs-toggle="tooltip" data-bs-placement="top"
                                    data-bs-title="Keys which has changed its original value after translated in target language">Changed</span>
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="done-keys-tab" data-bs-toggle="tab"
                                data-bs-target="#done-keys-tab-pane" type="button" role="tab"
                                aria-controls="done-keys-tab-pane" aria-selected="false">
                                <span data-bs-toggle="tooltip" data-bs-placement="top"
                                    data-bs-title="Keys which has already translated in target language">Done</span>
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="skipped-keys-tab" data-bs-toggle="tab"
                                data-bs-target="#skipped-keys-tab-pane" type="button" role="tab"
                                aria-controls="skipped-keys-tab-pane" aria-selected="false">
                                <span data-bs-toggle="tooltip" data-bs-placement="top"
                                    data-bs-title="Keys which is skipped, usually an alias key of another key">Skipped</span>
                            </button>
                        </li>
                    </ul>
                    <!-- Keys tab content -->
                    <div class="tab-content translation-keys-tab-content">
                        <div class="tab-pane fade show active" id="new-keys-tab-pane" role="tabpanel"
                            aria-labelledby="new-keys-tab" tabindex="0">
                            <ul id="translation-keys-new-key-list" class="list-group list-group-flush"></ul>
                        </div>
                        <div class="tab-pane fade" id="changed-keys-tab-pane" role="tabpanel"
                            aria-labelledby="changed-keys-tab" tabindex="1">
                            <ul id="translation-keys-changed-key-list" class="list-group list-group-flush"></ul>
                        </div>
                        <div class="tab-pane fade" id="done-keys-tab-pane" role="tabpanel"
                            aria-labelledby="done-keys-tab" tabindex="2">
                            <ul id="translation-keys-done-key-list" class="list-group list-group-flush"></ul>
                        </div>
                        <div class="tab-pane fade" id="skipped-keys-tab-pane" role="tabpanel"
                            aria-labelledby="skipped-keys-tab" tabindex="3">
                            <ul id="translation-keys-skipped-key-list" class="list-group list-group-flush"></ul>
                        </div>
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
                        <form id="translation-translate-form">
                            <input type="hidden" id="translation-translate-key">
                            <div class="mb-3">
                                <textarea id="input-translation-translate-value" class="form-control" rows="5" disabled
                                    placeholder="Translation"></textarea>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="" disabled
                                    id="checkbox-translation-translate-skipped">
                                <label class="form-check-label" for="translation-translate-skipped">
                                    Skip (Will not generate translation data)
                                </label>
                            </div>
                            <p id="translation-translate-update-time">Update time: Never</p>
                            <p>Attention: All " and \ will be automatically escaped</p>
                            <button id="btn-translation-submit" type="submit" class="btn btn-primary"
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
