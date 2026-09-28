/* =========================================================
   PocketSmart AI
   Main Frontend JavaScript
   ========================================================= */


/* =========================================================
   Global Helpers
   ========================================================= */

/**
 * Safely escape text before inserting it into HTML.
 */
function escapeHtml(value) {
    return String(value ?? "")
        .replace(/[&<>"']/g, function (character) {
            const entities = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            };

            return entities[character];
        });
}


/**
 * Format Indian Rupees.
 */
function formatCurrency(value) {
    const amount = Number(value || 0);

    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0
    }).format(amount);
}


/**
 * Display a loading message.
 */
function showLoading(container) {
    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="card loading">
            <span class="spinner"></span>
            <span>Generating your recommendations...</span>
        </div>
    `;
}


/**
 * Display an error message.
 */
function showError(container, message) {
    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="alert alert-error">
            ${escapeHtml(message)}
        </div>
    `;
}


/* =========================================================
   Mobile Navigation
   ========================================================= */

function initializeMobileMenu() {
    const menuButton =
        document.querySelector(".menu-button");

    const navLinks =
        document.querySelector(".nav-links");

    if (!menuButton || !navLinks) {
        return;
    }

    menuButton.addEventListener("click", function () {
        navLinks.classList.toggle("active");
    });
}


/* =========================================================
   Authentication Session
   ========================================================= */

async function loadSession() {
    const sessionElements =
        document.querySelectorAll("[data-session]");

    if (!sessionElements.length) {
        return;
    }

    try {
        const response = await fetch("/auth/session", {
            method: "GET",
            credentials: "same-origin"
        });

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        sessionElements.forEach(function (element) {
            if (data.logged_in && data.user) {
                element.textContent =
                    data.user.username;
            } else {
                element.textContent = "";
            }
        });

    } catch (error) {
        console.error(
            "Unable to load session:",
            error
        );
    }
}


/* =========================================================
   Form Data Conversion
   ========================================================= */

function formToObject(form) {
    const formData = new FormData(form);

    const data = {};

    formData.forEach(function (value, key) {
        if (data[key] !== undefined) {

            if (!Array.isArray(data[key])) {
                data[key] = [data[key]];
            }

            data[key].push(value);

        } else {
            data[key] = value;
        }
    });

    return data;
}


/**
 * Convert common numeric form values.
 */
function normalizeFormData(data) {

    const numericFields = [
        "budget",
        "guests",
        "people",
        "quantity",
        "days"
    ];

    numericFields.forEach(function (field) {

        if (
            data[field] !== undefined &&
            data[field] !== ""
        ) {
            const number = Number(data[field]);

            if (!Number.isNaN(number)) {
                data[field] = number;
            }
        }
    });

    return data;
}


/* =========================================================
   Recommendation Rendering
   ========================================================= */

function renderRecommendation(item) {

    if (!item || typeof item !== "object") {
        return "";
    }

    const name =
        item.name ||
        item.product_name ||
        item.title ||
        "Recommendation";

    const category =
        item.category ||
        item.type ||
        "Recommendation";

    const price =
        item.estimated_price_inr ??
        item.price_inr ??
        item.price;

    const reason =
        item.reason ||
        item.description ||
        item.why ||
        "";

    const platform =
        item.platform ||
        item.store ||
        "";

    const quantity =
        item.quantity ||
        "";

    const searchUrl =
        item.search_url ||
        item.url ||
        "";

    return `
        <article class="recommendation-card">

            <h3>
                ${escapeHtml(name)}
            </h3>

            <div class="recommendation-meta">

                <span class="badge">
                    ${escapeHtml(category)}
                </span>

                ${
                    quantity
                    ? `
                        <span class="badge">
                            Qty: ${escapeHtml(quantity)}
                        </span>
                    `
                    : ""
                }

            </div>

            ${
                price !== undefined &&
                price !== null &&
                price !== ""
                ? `
                    <p class="price">
                        ${formatCurrency(price)}
                    </p>
                `
                : ""
            }

            ${
                reason
                ? `
                    <p>
                        ${escapeHtml(reason)}
                    </p>
                `
                : ""
            }

            ${
                platform
                ? `
                    <p>
                        <strong>Platform:</strong>
                        ${escapeHtml(platform)}
                    </p>
                `
                : ""
            }

            ${
                searchUrl
                ? `
                    <div style="margin-top: 15px;">
                        <a
                            class="btn"
                            href="${escapeHtml(searchUrl)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            View / Search
                        </a>
                    </div>
                `
                : ""
            }

        </article>
    `;
}


/* =========================================================
   Budget Breakdown
   ========================================================= */

function renderBudgetBreakdown(breakdown) {

    if (
        !breakdown ||
        typeof breakdown !== "object"
    ) {
        return "";
    }

    const entries =
        Object.entries(breakdown);

    if (!entries.length) {
        return "";
    }

    return `
        <div class="budget-breakdown">

            ${entries.map(function ([key, value]) {

                return `
                    <div class="budget-item">

                        <span>
                            ${escapeHtml(
                                key
                                    .replace(/_/g, " ")
                                    .replace(
                                        /\b\w/g,
                                        function (letter) {
                                            return letter.toUpperCase();
                                        }
                                    )
                            )}
                        </span>

                        <strong>
                            ${formatCurrency(value)}
                        </strong>

                    </div>
                `;

            }).join("")}

        </div>
    `;
}


/* =========================================================
   Full Recommendation Results
   ========================================================= */

function renderResults(data, container) {

    if (!container) {
        return;
    }

    if (!data || typeof data !== "object") {
        showError(
            container,
            "The server returned an invalid response."
        );
        return;
    }

    const items =
        Array.isArray(data.items)
            ? data.items
            : Array.isArray(data.recommendations)
                ? data.recommendations
                : [];

    const summary =
        data.summary ||
        data.message ||
        "";

    let observationsHtml = "";

    if (
        Array.isArray(
            data.outfit_observations
        ) &&
        data.outfit_observations.length
    ) {

        observationsHtml = `
            <div class="card">

                <h3>
                    Outfit Observations
                </h3>

                <ul>
                    ${
                        data.outfit_observations
                            .map(function (observation) {
                                return `
                                    <li>
                                        ${escapeHtml(
                                            observation
                                        )}
                                    </li>
                                `;
                            })
                            .join("")
                    }
                </ul>

            </div>
        `;
    }

    const recommendationsHtml =
        items.length
            ? `
                <div class="results-grid">
                    ${
                        items
                            .map(renderRecommendation)
                            .join("")
                    }
                </div>
            `
            : `
                <div class="card empty-state">
                    <p>
                        No individual recommendations
                        were returned.
                    </p>
                </div>
            `;

    container.innerHTML = `

        <div class="results-container">

            <div class="card results-header">

                <h2>
                    Recommendation Plan
                </h2>

                ${
                    summary
                    ? `
                        <p>
                            ${escapeHtml(summary)}
                        </p>
                    `
                    : ""
                }

            </div>

            ${
                renderBudgetBreakdown(
                    data.budget_breakdown
                )
            }

            ${observationsHtml}

            ${recommendationsHtml}

        </div>
    `;
}


/* =========================================================
   Planner Forms
   ========================================================= */

function initializePlannerForms() {

    const forms =
        document.querySelectorAll(
            ".planner-form"
        );

    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();

                const endpoint =
                    form.dataset.endpoint;

                const resultSelector =
                    form.dataset.result ||
                    "#results";

                const resultContainer =
                    document.querySelector(
                        resultSelector
                    );

                const submitButton =
                    form.querySelector(
                        "button[type='submit']"
                    );

                if (!endpoint) {

                    showError(
                        resultContainer,
                        "Planner endpoint is missing."
                    );

                    return;
                }

                if (submitButton) {

                    submitButton.disabled =
                        true;

                    submitButton.dataset
                        .originalText =
                        submitButton.textContent;

                    submitButton.textContent =
                        "Generating...";
                }

                showLoading(
                    resultContainer
                );

                try {

                    let response;

                    /*
                     * If the form contains a file,
                     * send multipart/form-data.
                     */

                    if (
                        form.enctype ===
                        "multipart/form-data"
                    ) {

                        const formData =
                            new FormData(form);

                        response =
                            await fetch(
                                endpoint,
                                {
                                    method: "POST",
                                    credentials:
                                        "same-origin",
                                    body: formData
                                }
                            );

                    } else {

                        const formData =
                            formToObject(form);

                        const data =
                            normalizeFormData(
                                formData
                            );

                        response =
                            await fetch(
                                endpoint,
                                {
                                    method: "POST",

                                    credentials:
                                        "same-origin",

                                    headers: {
                                        "Content-Type":
                                            "application/json"
                                    },

                                    body:
                                        JSON.stringify(
                                            data
                                        )
                                }
                            );
                    }

                    const contentType =
                        response.headers.get(
                            "content-type"
                        ) || "";

                    let data;

                    if (
                        contentType.includes(
                            "application/json"
                        )
                    ) {

                        data =
                            await response.json();

                    } else {

                        const text =
                            await response.text();

                        data = {
                            detail: text
                        };
                    }

                    if (!response.ok) {

                        throw new Error(
                            data.detail ||
                            data.message ||
                            "Unable to generate recommendations."
                        );
                    }

                    renderResults(
                        data,
                        resultContainer
                    );

                } catch (error) {

                    console.error(
                        "Planner error:",
                        error
                    );

                    showError(
                        resultContainer,
                        error.message ||
                        "Something went wrong."
                    );

                } finally {

                    if (submitButton) {

                        submitButton.disabled =
                            false;

                        submitButton.textContent =
                            submitButton.dataset
                                .originalText ||
                            "Generate Recommendations";
                    }
                }
            }
        );
    });
}


/* =========================================================
   Generic API Request
   ========================================================= */

async function apiRequest(
    url,
    options = {}
) {

    const response =
        await fetch(
            url,
            {
                credentials: "same-origin",
                ...options
            }
        );

    const contentType =
        response.headers.get(
            "content-type"
        ) || "";

    let data;

    if (
        contentType.includes(
            "application/json"
        )
    ) {

        data =
            await response.json();

    } else {

        data =
            await response.text();
    }

    if (!response.ok) {

        const message =
            typeof data === "object"
                ? (
                    data.detail ||
                    data.message
                )
                : data;

        throw new Error(
            message ||
            "Request failed."
        );
    }

    return data;
}


/* =========================================================
   Image Upload Preview
   ========================================================= */

function initializeImagePreview() {

    const inputs =
        document.querySelectorAll(
            "[data-image-input]"
        );

    inputs.forEach(function (input) {

        const previewSelector =
            input.dataset.preview ||
            "[data-image-preview]";

        const preview =
            document.querySelector(
                previewSelector
            );

        if (!preview) {
            return;
        }

        input.addEventListener(
            "change",
            function () {

                const file =
                    input.files &&
                    input.files[0];

                preview.innerHTML = "";

                if (!file) {
                    return;
                }

                if (
                    !file.type.startsWith(
                        "image/"
                    )
                ) {

                    preview.innerHTML = `
                        <div class="alert alert-error">
                            Please select a valid image.
                        </div>
                    `;

                    input.value = "";

                    return;
                }

                const imageUrl =
                    URL.createObjectURL(file);

                preview.innerHTML = `
                    <div class="card">

                        <p>
                            Image Preview
                        </p>

                        <img
                            src="${imageUrl}"
                            alt="Uploaded preview"
                            style="
                                max-width: 100%;
                                max-height: 350px;
                                margin-top: 12px;
                                border-radius: 10px;
                                display: block;
                            "
                        >

                    </div>
                `;
            }
        );
    });
}


/* =========================================================
   Login Form
   ========================================================= */

function initializeLoginForm() {

    const form =
        document.querySelector(
            "#login-form"
        );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async function (event) {

            /*
             * Allow the normal HTML form submission
             * when no JavaScript-specific login handler
             * is requested.
             */

            if (
                form.dataset.ajax !== "true"
            ) {
                return;
            }

            event.preventDefault();

            const errorContainer =
                document.querySelector(
                    "#login-error"
                );

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            try {

                if (button) {
                    button.disabled = true;
                    button.textContent =
                        "Signing in...";
                }

                const formData =
                    new FormData(form);

                const response =
                    await fetch(
                        form.action ||
                        "/auth/login",
                        {
                            method: "POST",
                            credentials:
                                "same-origin",
                            body: formData
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Invalid email or password."
                    );
                }

                window.location.href =
                    "/dashboard";

            } catch (error) {

                if (errorContainer) {

                    errorContainer.innerHTML = `
                        <div class="alert alert-error">
                            ${escapeHtml(
                                error.message
                            )}
                        </div>
                    `;

                }

            } finally {

                if (button) {
                    button.disabled = false;
                    button.textContent =
                        "Login";
                }
            }
        }
    );
}


/* =========================================================
   Registration Form
   ========================================================= */

function initializeRegisterForm() {

    const form =
        document.querySelector(
            "#register-form"
        );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async function (event) {

            if (
                form.dataset.ajax !== "true"
            ) {
                return;
            }

            event.preventDefault();

            const errorContainer =
                document.querySelector(
                    "#register-error"
                );

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            try {

                if (button) {
                    button.disabled = true;
                    button.textContent =
                        "Creating account...";
                }

                const formData =
                    new FormData(form);

                const response =
                    await fetch(
                        form.action ||
                        "/auth/register",
                        {
                            method: "POST",
                            credentials:
                                "same-origin",
                            body: formData
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Registration failed."
                    );
                }

                window.location.href =
                    "/login?registered=1";

            } catch (error) {

                if (errorContainer) {

                    errorContainer.innerHTML = `
                        <div class="alert alert-error">
                            ${escapeHtml(
                                error.message
                            )}
                        </div>
                    `;

                }

            } finally {

                if (button) {
                    button.disabled = false;
                    button.textContent =
                        "Create Account";
                }
            }
        }
    );
}


/* =========================================================
   Password Confirmation
   ========================================================= */

function initializePasswordConfirmation() {

    const form =
        document.querySelector(
            "#register-form"
        );

    if (!form) {
        return;
    }

    const password =
        form.querySelector(
            "input[name='password']"
        );

    const confirmPassword =
        form.querySelector(
            "input[name='confirm_password']"
        );

    if (
        !password ||
        !confirmPassword
    ) {
        return;
    }

    form.addEventListener(
        "submit",
        function (event) {

            if (
                password.value !==
                confirmPassword.value
            ) {

                event.preventDefault();

                const errorContainer =
                    document.querySelector(
                        "#register-error"
                    );

                if (errorContainer) {

                    errorContainer.innerHTML = `
                        <div class="alert alert-error">
                            Passwords do not match.
                        </div>
                    `;
                }
            }
        }
    );
}


/* =========================================================
   Delete / Confirmation Buttons
   ========================================================= */

function initializeConfirmActions() {

    const elements =
        document.querySelectorAll(
            "[data-confirm]"
        );

    elements.forEach(function (element) {

        element.addEventListener(
            "click",
            function (event) {

                const message =
                    element.dataset.confirm ||
                    "Are you sure?";

                if (!window.confirm(message)) {
                    event.preventDefault();
                }
            }
        );
    });
}


/* =========================================================
   Auto Hide Alerts
   ========================================================= */

function initializeAlerts() {

    const alerts =
        document.querySelectorAll(
            ".alert[data-auto-hide]"
        );

    alerts.forEach(function (alert) {

        const duration =
            Number(
                alert.dataset.autoHide
            ) || 4000;

        setTimeout(
            function () {

                alert.style.transition =
                    "opacity 0.3s ease";

                alert.style.opacity = "0";

                setTimeout(
                    function () {
                        alert.remove();
                    },
                    300
                );

            },
            duration
        );
    });
}


/* =========================================================
   Application Initialization
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeMobileMenu();

        loadSession();

        initializePlannerForms();

        initializeImagePreview();

        initializeLoginForm();

        initializeRegisterForm();

        initializePasswordConfirmation();

        initializeConfirmActions();

        initializeAlerts();

    }
);