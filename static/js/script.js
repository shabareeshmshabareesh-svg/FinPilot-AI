// ============================================================
// FINPILOT AI
// GLOBAL SCRIPT.JS
// ============================================================

console.log("🚀 FinPilot AI Loaded Successfully");


// ============================================================
// CSRF TOKEN HELPER
// ============================================================
//
// Flask-WTF requires a valid CSRF token on every
// POST request.
//
// templates/base.html renders the token into a meta
// tag and this helper reads it back for the AJAX
// calls made from this file.

function finPilotCSRFToken() {

    const meta =
        document.querySelector(
            "meta[name='csrf-token']"
        );


    return meta
        ? meta.getAttribute("content")
        : "";
}


// ============================================================
// CSRF HEADERS
// ============================================================

function finPilotCSRFHeaders() {

    const token =
        finPilotCSRFToken();


    return token
        ? {"X-CSRFToken": token}
        : {};
}


document.addEventListener("DOMContentLoaded", function () {

    console.log("🧠 FinPilot AI Frontend Ready");


    // ========================================================
    // 1. SMOOTH SCROLL
    // ========================================================

    document
        .querySelectorAll('a[href^="#"]')
        .forEach(function (anchor) {

            anchor.addEventListener("click", function (event) {

                const targetSelector =
                    this.getAttribute("href");

                if (
                    !targetSelector ||
                    targetSelector === "#"
                ) {
                    return;
                }

                const target =
                    document.querySelector(
                        targetSelector
                    );

                if (target) {

                    event.preventDefault();

                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            });
        });


    // ========================================================
    // 2. DASHBOARD MONEY COUNTERS
    // ========================================================

    const counters =
        document.querySelectorAll(".counter");


    counters.forEach(function (counter) {

        const target =
            parseFloat(
                counter.dataset.value || 0
            );


        if (
            Number.isNaN(target) ||
            !Number.isFinite(target)
        ) {

            counter.textContent = "₹0";

            return;
        }


        const duration = 900;

        const startTime =
            performance.now();


        function animate(currentTime) {

            const elapsed =
                currentTime - startTime;


            const progress =
                Math.min(
                    elapsed / duration,
                    1
                );


            const eased =
                1 -
                Math.pow(
                    1 - progress,
                    3
                );


            const currentValue =
                target * eased;


            counter.textContent =
                "₹" +
                Math.round(
                    currentValue
                ).toLocaleString("en-IN");


            if (progress < 1) {

                requestAnimationFrame(
                    animate
                );

            } else {

                counter.textContent =
                    "₹" +
                    Math.round(
                        target
                    ).toLocaleString("en-IN");
            }
        }


        requestAnimationFrame(
            animate
        );
    });


    // ========================================================
    // 3. SMART COACH
    // ========================================================

    const smartCoach =
        document.querySelector(
            ".smart-coach-panel"
        );


    if (smartCoach) {

        smartCoach.classList.add(
            "smart-coach-ready"
        );

        smartCoach.setAttribute(
            "aria-live",
            "polite"
        );

        console.log(
            "🧠 Smart Coach detected"
        );
    }


    // ========================================================
    // 4. AI INSIGHT CARDS
    // ========================================================

    document
        .querySelectorAll(".smart-insight")
        .forEach(function (card, index) {

            card.style.animationDelay =
                (index * 80) + "ms";
        });


    // ========================================================
    // 5. SMART ALERT CARDS
    // ========================================================

    document
        .querySelectorAll(".smart-alert")
        .forEach(function (alert, index) {

            alert.style.animationDelay =
                (index * 70) + "ms";
        });


    // ========================================================
    // 6. INTERSECTION ANIMATION
    // ========================================================

    const animatedElements =
        document.querySelectorAll(
            ".finance-card, " +
            ".dashboard-panel, " +
            ".smart-alert, " +
            ".smart-insight, " +
            ".smart-coach-panel"
        );


    if (
        "IntersectionObserver" in window
    ) {

        const observer =
            new IntersectionObserver(
                function (entries) {

                    entries.forEach(
                        function (entry) {

                            if (
                                entry.isIntersecting
                            ) {

                                entry.target.classList.add(
                                    "fp-visible"
                                );

                                observer.unobserve(
                                    entry.target
                                );
                            }
                        }
                    );
                },
                {
                    threshold: 0.08
                }
            );


        animatedElements.forEach(
            function (element) {

                observer.observe(
                    element
                );
            }
        );

    } else {

        animatedElements.forEach(
            function (element) {

                element.classList.add(
                    "fp-visible"
                );
            }
        );
    }


    // ========================================================
    // 7. FINPILOT AI ELEMENTS
    // ========================================================

    const aiToggle =
        document.getElementById(
            "finpilot-ai-toggle"
        );


    const aiPanel =
        document.getElementById(
            "finpilot-ai-panel"
        );


    const aiClose =
        document.getElementById(
            "finpilot-ai-close"
        );


    const aiForm =
        document.getElementById(
            "finpilot-ai-form"
        );


    const aiInput =
        document.getElementById(
            "finpilot-ai-input"
        );


    const aiMessages =
        document.getElementById(
            "finpilot-ai-messages"
        );


    const aiSend =
        document.getElementById(
            "finpilot-ai-send"
        );


    const quickQuestions =
        document.getElementById(
            "finpilot-ai-quick"
        );


    // ========================================================
    // 8. FORMAT AI TEXT
    // ========================================================

    function formatAIText(value) {

        if (
            value === null ||
            value === undefined
        ) {
            return "";
        }


        let text =
            String(value);


        // Windows line endings

        text =
            text.replace(
                /\r\n/g,
                "\n"
            );


        // Standalone carriage return

        text =
            text.replace(
                /\r/g,
                "\n"
            );


        // Literal escaped newline

        text =
            text.replace(
                /\\n/g,
                "\n"
            );


        // Literal escaped tab

        text =
            text.replace(
                /\\t/g,
                "    "
            );


        // Remove excessive blank lines

        text =
            text.replace(
                /\n{3,}/g,
                "\n\n"
            );


        return text.trim();
    }


    // ========================================================
    // 9. FORMAT INLINE TEXT
    // Supports **bold**
    // ========================================================

    function appendFormattedInlineText(
        element,
        text
    ) {

        if (!text) {
            return;
        }


        const parts =
            String(text).split(
                /(\*\*[^*]+\*\*)/
            );


        parts.forEach(
            function (part) {

                if (
                    part.startsWith("**") &&
                    part.endsWith("**")
                ) {

                    const bold =
                        document.createElement(
                            "strong"
                        );


                    bold.textContent =
                        part.substring(
                            2,
                            part.length - 2
                        );


                    element.appendChild(
                        bold
                    );

                } else {

                    element.appendChild(
                        document.createTextNode(
                            part
                        )
                    );
                }
            }
        );
    }


    // ========================================================
    // 10. SCROLL AI CHAT
    // ========================================================

    function scrollAIToBottom() {

        if (!aiMessages) {
            return;
        }


        aiMessages.scrollTo({
            top:
                aiMessages.scrollHeight,
            behavior:
                "smooth"
        });
    }


    // ========================================================
    // 11. OPEN AI
    // ========================================================

    function openFinPilotAI() {

        if (!aiPanel) {
            return;
        }


        aiPanel.classList.add(
            "active"
        );


        aiPanel.setAttribute(
            "aria-hidden",
            "false"
        );


        if (aiToggle) {

            aiToggle.setAttribute(
                "aria-expanded",
                "true"
            );
        }


        setTimeout(
            function () {

                if (aiInput) {
                    aiInput.focus();
                }

            },
            200
        );
    }


    // ========================================================
    // 12. CLOSE AI
    // ========================================================

    function closeFinPilotAI() {

        if (!aiPanel) {
            return;
        }


        aiPanel.classList.remove(
            "active"
        );


        aiPanel.setAttribute(
            "aria-hidden",
            "true"
        );


        if (aiToggle) {

            aiToggle.setAttribute(
                "aria-expanded",
                "false"
            );
        }
    }


    // ========================================================
    // 13. AI TOGGLE
    // ========================================================

    if (aiToggle) {

        aiToggle.setAttribute(
            "aria-expanded",
            "false"
        );


        aiToggle.addEventListener(
            "click",
            function () {

                if (
                    aiPanel &&
                    aiPanel.classList.contains(
                        "active"
                    )
                ) {

                    closeFinPilotAI();

                } else {

                    openFinPilotAI();
                }
            }
        );
    }


    // ========================================================
    // 14. AI CLOSE BUTTON
    // ========================================================

    if (aiClose) {

        aiClose.addEventListener(
            "click",
            function () {

                closeFinPilotAI();

            }
        );
    }


    // ========================================================
    // 15. SET QUESTION
    // ========================================================

    function setQuestion(question) {

        if (!aiInput) {
            return;
        }


        aiInput.value =
            question || "";


        aiInput.focus();
    }


    // Make available globally
    window.setFinPilotQuestion =
        setQuestion;


    // ========================================================
    // 16. ADD USER MESSAGE
    // ========================================================

    function addUserMessage(
        message
    ) {

        if (!aiMessages) {
            return;
        }


        const wrapper =
            document.createElement(
                "div"
            );


        wrapper.className =
            "finpilot-message " +
            "finpilot-message-user";


        const content =
            document.createElement(
                "div"
            );


        content.className =
            "finpilot-message-content";


        const text =
            document.createElement(
                "p"
            );


        text.textContent =
            message;


        text.style.whiteSpace =
            "pre-wrap";


        content.appendChild(
            text
        );


        wrapper.appendChild(
            content
        );


        aiMessages.appendChild(
            wrapper
        );


        scrollAIToBottom();
    }


    // ========================================================
    // 17. COPY FALLBACK
    // ========================================================

    async function copyText(text) {

        const cleanText =
            formatAIText(
                text || ""
            );


        // Modern clipboard

        if (
            navigator.clipboard &&
            window.isSecureContext
        ) {

            await navigator.clipboard.writeText(
                cleanText
            );

            return true;
        }


        // Fallback

        const textarea =
            document.createElement(
                "textarea"
            );


        textarea.value =
            cleanText;


        textarea.style.position =
            "fixed";


        textarea.style.left =
            "-9999px";


        textarea.style.top =
            "0";


        document.body.appendChild(
            textarea
        );


        textarea.focus();


        textarea.select();


        let successful =
            false;


        try {

            successful =
                document.execCommand(
                    "copy"
                );

        } catch (error) {

            console.error(
                "Clipboard fallback failed:",
                error
            );

        }


        textarea.remove();


        if (!successful) {

            throw new Error(
                "Copy operation failed."
            );
        }


        return true;
    }


    // ========================================================
    // 18. GLOBAL AI RESPONSE ACTIONS
    //
    // Copy
    // Helpful
    // Not helpful
    // ========================================================

    function createGlobalAIResponseActions(
        responseText,
        messageId,
        existingFeedback
    ) {

        const actionBar =
            document.createElement(
                "div"
            );


        actionBar.className =
            "finpilot-ai-response-actions";


        actionBar.style.display =
            "flex";


        actionBar.style.flexWrap =
            "wrap";


        actionBar.style.alignItems =
            "center";


        actionBar.style.gap =
            "6px";


        actionBar.style.marginTop =
            "10px";


        // ----------------------------------------------------
        // BUTTON CREATOR
        // ----------------------------------------------------

        function createButton(
            label,
            action
        ) {

            const button =
                document.createElement(
                    "button"
                );


            button.type =
                "button";


            button.textContent =
                label;


            button.dataset.action =
                action;


            button.style.border =
                "1px solid rgba(108,117,125,0.25)";


            button.style.background =
                "transparent";


            button.style.color =
                "inherit";


            button.style.borderRadius =
                "8px";


            button.style.padding =
                "5px 9px";


            button.style.fontSize =
                "0.76rem";


            button.style.lineHeight =
                "1.2";


            button.style.cursor =
                "pointer";


            button.style.transition =
                "all 0.18s ease";


            button.addEventListener(
                "mouseenter",
                function () {

                    if (
                        !button.classList.contains(
                            "finpilot-feedback-active"
                        )
                    ) {

                        button.style.background =
                            "rgba(13,110,253,0.08)";
                    }
                }
            );


            button.addEventListener(
                "mouseleave",
                function () {

                    if (
                        !button.classList.contains(
                            "finpilot-feedback-active"
                        )
                    ) {

                        button.style.background =
                            "transparent";
                    }
                }
            );


            return button;
        }


        // ----------------------------------------------------
        // COPY BUTTON
        // ----------------------------------------------------

        const copyButton =
            createButton(
                "📋 Copy",
                "copy"
            );


        copyButton.title =
            "Copy AI response";


        copyButton.addEventListener(
            "click",
            async function () {

                try {

                    await copyText(
                        responseText
                    );


                    copyButton.textContent =
                        "✅ Copied";


                    copyButton.style.background =
                        "rgba(25,135,84,0.10)";


                    setTimeout(
                        function () {

                            copyButton.textContent =
                                "📋 Copy";


                            copyButton.style.background =
                                "transparent";

                        },
                        1500
                    );

                } catch (error) {

                    console.error(
                        "FinPilot copy failed:",
                        error
                    );


                    copyButton.textContent =
                        "⚠️ Copy failed";


                    setTimeout(
                        function () {

                            copyButton.textContent =
                                "📋 Copy";

                        },
                        1500
                    );
                }
            }
        );


        // ----------------------------------------------------
        // HELPFUL BUTTON
        // ----------------------------------------------------

        const helpfulButton =
            createButton(
                "👍 Helpful",
                "helpful"
            );


        helpfulButton.title =
            "Mark response helpful";


        // ----------------------------------------------------
        // NOT HELPFUL BUTTON
        // ----------------------------------------------------

        const notHelpfulButton =
            createButton(
                "👎 Not helpful",
                "not_helpful"
            );


        notHelpfulButton.title =
            "Mark response not helpful";


        // ----------------------------------------------------
        // STATUS
        // ----------------------------------------------------

        const status =
            document.createElement(
                "span"
            );


        status.className =
            "finpilot-feedback-status";


        status.style.fontSize =
            "0.76rem";


        status.style.color =
            "#6c757d";


        status.style.marginLeft =
            "2px";


        status.setAttribute(
            "aria-live",
            "polite"
        );


        // ----------------------------------------------------
        // RESTORE EXISTING FEEDBACK
        // ----------------------------------------------------

        function activateButton(
            button
        ) {

            button.classList.add(
                "finpilot-feedback-active"
            );


            button.style.background =
                "rgba(13,110,253,0.10)";
        }


        if (
            existingFeedback ===
            "helpful"
        ) {

            activateButton(
                helpfulButton
            );
        }


        if (
            existingFeedback ===
            "not_helpful"
        ) {

            activateButton(
                notHelpfulButton
            );
        }


        // ----------------------------------------------------
        // SAVE FEEDBACK
        // ----------------------------------------------------

        async function submitFeedback(
            feedback
        ) {

            if (!messageId) {

                status.textContent =
                    "Feedback unavailable";


                console.warn(
                    "FinPilot: message_id missing."
                );


                return;
            }


            helpfulButton.disabled =
                true;


            notHelpfulButton.disabled =
                true;


            status.textContent =
                "Saving...";


            try {

                const formData =
                    new FormData();


                formData.append(
                    "message_id",
                    String(messageId)
                );


                formData.append(
                    "feedback",
                    feedback
                );


                const response =
                    await fetch(
                        "/coach/feedback",
                        {
                            method:
                                "POST",

                            body:
                                formData,

                            headers: {
                                "X-Requested-With":
                                    "XMLHttpRequest",

                                "Accept":
                                    "application/json",

                                "X-CSRFToken":
                                    finPilotCSRFToken()
                            },

                            credentials:
                                "same-origin"
                        }
                    );


                const contentType =
                    response.headers.get(
                        "content-type"
                    ) || "";


                if (
                    !contentType.includes(
                        "application/json"
                    )
                ) {

                    throw new Error(
                        "Server returned a non-JSON response."
                    );
                }


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.error ||
                        "Unable to save feedback."
                    );
                }


                // Reset both buttons

                helpfulButton.classList.remove(
                    "finpilot-feedback-active"
                );


                notHelpfulButton.classList.remove(
                    "finpilot-feedback-active"
                );


                helpfulButton.style.background =
                    "transparent";


                notHelpfulButton.style.background =
                    "transparent";


                // Activate selected button

                if (
                    feedback ===
                    "helpful"
                ) {

                    activateButton(
                        helpfulButton
                    );


                    status.textContent =
                        "Thanks! 👍";

                } else {

                    activateButton(
                        notHelpfulButton
                    );


                    status.textContent =
                        "Thanks for the feedback.";
                }


            } catch (error) {

                console.error(
                    "FinPilot feedback error:",
                    error
                );


                status.textContent =
                    "Could not save feedback.";

            } finally {

                helpfulButton.disabled =
                    false;


                notHelpfulButton.disabled =
                    false;
            }
        }


        // ----------------------------------------------------
        // FEEDBACK EVENTS
        // ----------------------------------------------------

        helpfulButton.addEventListener(
            "click",
            function () {

                submitFeedback(
                    "helpful"
                );

            }
        );


        notHelpfulButton.addEventListener(
            "click",
            function () {

                submitFeedback(
                    "not_helpful"
                );

            }
        );


        // ----------------------------------------------------
        // APPEND BUTTONS
        // ----------------------------------------------------

        actionBar.appendChild(
            copyButton
        );


        actionBar.appendChild(
            helpfulButton
        );


        actionBar.appendChild(
            notHelpfulButton
        );


        actionBar.appendChild(
            status
        );


        return actionBar;
    }


    // ========================================================
    // 19. ADD AI MESSAGE
    // ========================================================

    function addAIMessage(
        data
    ) {

        if (!aiMessages) {
            return;
        }


        const wrapper =
            document.createElement(
                "div"
            );


        wrapper.className =
            "finpilot-message " +
            "finpilot-message-ai";


        const avatar =
            document.createElement(
                "div"
            );


        avatar.className =
            "finpilot-message-avatar";


        avatar.textContent =
            data.icon ||
            "🤖";


        const content =
            document.createElement(
                "div"
            );


        content.className =
            "finpilot-message-content";


        const title =
            document.createElement(
                "strong"
            );


        title.textContent =
            data.title ||
            "FinPilot AI";


        const message =
            document.createElement(
                "div"
            );


        message.className =
            "finpilot-ai-response-text";


        const rawMessage =
            data.message ||
            data.response ||
            data.answer ||
            "I couldn't generate an answer.";


        const formattedText =
            formatAIText(
                rawMessage
            );


        const lines =
            formattedText.split(
                "\n"
            );


        lines.forEach(
            function (line, index) {

                const cleanLine =
                    line.trim();


                if (!cleanLine) {

                    if (
                        index <
                        lines.length - 1
                    ) {

                        const spacer =
                            document.createElement(
                                "div"
                            );


                        spacer.style.height =
                            "8px";


                        message.appendChild(
                            spacer
                        );
                    }


                    return;
                }


                const lineElement =
                    document.createElement(
                        "div"
                    );


                // Numbered list

                const numberedMatch =
                    cleanLine.match(
                        /^(\d+)\.\s+(.*)$/
                    );


                if (numberedMatch) {

                    const number =
                        document.createElement(
                            "span"
                        );


                    number.textContent =
                        numberedMatch[1] +
                        ". ";


                    number.style.fontWeight =
                        "700";


                    number.style.color =
                        "#1769ff";


                    lineElement.appendChild(
                        number
                    );


                    appendFormattedInlineText(
                        lineElement,
                        numberedMatch[2]
                    );

                }

                // Bullet list

                else if (
                    cleanLine.startsWith("- ") ||
                    cleanLine.startsWith("• ")
                ) {

                    const bullet =
                        document.createElement(
                            "span"
                        );


                    bullet.textContent =
                        "• ";


                    bullet.style.fontWeight =
                        "700";


                    bullet.style.color =
                        "#1769ff";


                    lineElement.appendChild(
                        bullet
                    );


                    appendFormattedInlineText(
                        lineElement,
                        cleanLine.substring(2)
                    );

                }

                // Normal text

                else {

                    appendFormattedInlineText(
                        lineElement,
                        cleanLine
                    );
                }


                message.appendChild(
                    lineElement
                );
            }
        );


        message.style.lineHeight =
            "1.65";


        message.style.wordBreak =
            "break-word";


        message.style.marginTop =
            "6px";


        // ====================================================
        // IMPORTANT:
        // CREATE FEEDBACK BUTTONS HERE
        // ====================================================

        const actionBar =
            createGlobalAIResponseActions(
                rawMessage,
                data.message_id ||
                null,
                data.feedback ||
                ""
            );


        // ====================================================
        // APPEND CONTENT
        // ====================================================

        content.appendChild(
            title
        );


        content.appendChild(
            message
        );


        content.appendChild(
            actionBar
        );


        wrapper.appendChild(
            avatar
        );


        wrapper.appendChild(
            content
        );


        aiMessages.appendChild(
            wrapper
        );


        scrollAIToBottom();
    }


    // ========================================================
    // 20. SHOW TYPING
    // ========================================================

    function showTyping() {

        if (!aiMessages) {
            return null;
        }


        const wrapper =
            document.createElement(
                "div"
            );


        wrapper.className =
            "finpilot-message " +
            "finpilot-message-ai";


        wrapper.id =
            "finpilot-ai-typing";


        const avatar =
            document.createElement(
                "div"
            );


        avatar.className =
            "finpilot-message-avatar";


        avatar.textContent =
            "🤖";


        const content =
            document.createElement(
                "div"
            );


        content.className =
            "finpilot-message-content";


        const title =
            document.createElement(
                "strong"
            );


        title.textContent =
            "FinPilot AI";


        const bubble =
            document.createElement(
                "div"
            );


        bubble.className =
            "finpilot-thinking";


        bubble.innerHTML =
            `
                <span>
                    FinPilot is thinking
                </span>

                <span
                    class="thinking-dots"
                    style="
                        display:inline-flex;
                        gap:4px;
                        margin-left:5px;
                    "
                >
                    <span>•</span>
                    <span>•</span>
                    <span>•</span>
                </span>
            `;


        content.appendChild(
            title
        );


        content.appendChild(
            bubble
        );


        wrapper.appendChild(
            avatar
        );


        wrapper.appendChild(
            content
        );


        aiMessages.appendChild(
            wrapper
        );


        scrollAIToBottom();


        return wrapper;
    }


    // ========================================================
    // 21. REMOVE TYPING
    // ========================================================

    function removeTyping() {

        const typing =
            document.getElementById(
                "finpilot-ai-typing"
            );


        if (typing) {
            typing.remove();
        }
    }


    // ========================================================
    // 22. AI LOADING STATE
    // ========================================================

    function setAILoading(
        loading
    ) {

        if (aiInput) {

            aiInput.disabled =
                loading;
        }


        if (aiSend) {

            aiSend.disabled =
                loading;


            aiSend.innerHTML =
                loading
                    ? "⏳"
                    : "➤";
        }
    }


    // ========================================================
    // 23. ASK FINPILOT
    // ========================================================

    async function askFinpilot(
        question
    ) {

        if (!aiInput || !aiMessages) {
            return;
        }


        const cleanQuestion =
            String(
                question || ""
            ).trim();


        if (!cleanQuestion) {
            return;
        }


        if (
            aiInput.disabled
        ) {
            return;
        }


        // Open AI panel

        openFinPilotAI();


        // User message

        addUserMessage(
            cleanQuestion
        );


        // Clear input

        aiInput.value =
            "";


        // Hide quick questions

        if (quickQuestions) {

            quickQuestions.style.display =
                "none";
        }


        // Loading

        const typing =
            showTyping();


        setAILoading(
            true
        );


        try {

            const formData =
                new FormData();


            formData.append(
                "question",
                cleanQuestion
            );


            // =================================================
            // CSRF TOKEN (REQUEST BODY)
            // =================================================
            //
            // The X-CSRFToken header below already carries
            // the token from the base.html meta tag.
            //
            // Also append it to the form body so this POST
            // includes the valid Flask-WTF token in the
            // request body as well, matching the hidden
            // csrf_token inputs used by the project forms.

            formData.append(
                "csrf_token",
                finPilotCSRFToken()
            );


            // =================================================
            // SEND TO FLASK
            // =================================================

            const response =
                await fetch(
                    "/analytics/ask",
                    {
                        method:
                            "POST",

                        body:
                            formData,

                        headers: {
                            "X-Requested-With":
                                "XMLHttpRequest",

                            "Accept":
                                "application/json",

                            "X-CSRFToken":
                                finPilotCSRFToken()
                        },

                        credentials:
                            "same-origin"
                    }
                );


            // Remove typing

            if (typing) {
                typing.remove();
            }


            // =================================================
            // LOGIN REDIRECT
            // =================================================

            if (
                response.redirected
            ) {

                addAIMessage({

                    icon:
                        "🔐",

                    title:
                        "Login Required",

                    message:
                        "Please log in to use FinPilot AI."

                });


                return;
            }


            // =================================================
            // CONTENT TYPE
            // =================================================

            const contentType =
                response.headers.get(
                    "content-type"
                ) || "";


            if (
                !contentType.includes(
                    "application/json"
                )
            ) {

                addAIMessage({

                    icon:
                        "⚠️",

                    title:
                        "Unexpected Response",

                    message:
                        "FinPilot received an unexpected response. Please refresh the page and try again."

                });


                return;
            }


            const data =
                await response.json();


            console.log(
                "🤖 FinPilot AI Response:",
                data
            );


            // =================================================
            // SUCCESS
            // =================================================

            if (
                response.ok &&
                data.success
            ) {

                addAIMessage(
                    data
                );

            } else {

                addAIMessage({

                    icon:
                        "⚠️",

                    title:
                        data.title ||
                        "FinPilot AI",

                    message:
                        data.message ||
                        data.error ||
                        data.response ||
                        "Something went wrong. Please try again."

                });
            }


        } catch (error) {

            console.error(
                "❌ FinPilot AI Error:",
                error
            );


            removeTyping();


            addAIMessage({

                icon:
                    "⚠️",

                title:
                    "Connection Problem",

                message:
                    "I couldn't connect to FinPilot AI right now. Please check your connection and try again."

            });


        } finally {

            setAILoading(
                false
            );


            if (aiInput) {
                aiInput.focus();
            }
        }
    }


    // ========================================================
    // 24. AI FORM SUBMIT
    // ========================================================

    if (aiForm) {

        aiForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();


                const question =
                    aiInput
                        ? aiInput.value.trim()
                        : "";


                if (!question) {

                    if (aiInput) {
                        aiInput.focus();
                    }

                    return;
                }


                askFinpilot(
                    question
                );
            }
        );
    }


    // ========================================================
    // 25. QUICK QUESTIONS
    // ========================================================

    document
        .querySelectorAll(
            ".finpilot-quick-btn"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const question =
                            this.dataset.question;


                        if (!question) {
                            return;
                        }


                        askFinpilot(
                            question
                        );
                    }
                );
            }
        );


    // ========================================================
    // 26. ENTER KEY
    // ========================================================

    if (aiInput) {

        aiInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();


                    if (
                        !aiInput.disabled &&
                        aiForm
                    ) {

                        aiForm.requestSubmit();
                    }
                }
            }
        );
    }


    // ========================================================
    // 27. ESCAPE KEY
    // ========================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                aiPanel &&
                aiPanel.classList.contains(
                    "active"
                )
            ) {

                closeFinPilotAI();
            }
        }
    );


    // ========================================================
    // 28. CLICK OUTSIDE AI
    // ========================================================

    document.addEventListener(
        "click",
        function (event) {

            if (
                !aiPanel ||
                !aiToggle
            ) {
                return;
            }


            if (
                !aiPanel.classList.contains(
                    "active"
                )
            ) {
                return;
            }


            const clickedInsidePanel =
                aiPanel.contains(
                    event.target
                );


            const clickedToggle =
                aiToggle.contains(
                    event.target
                );


            if (
                !clickedInsidePanel &&
                !clickedToggle
            ) {

                closeFinPilotAI();
            }
        }
    );


    // ========================================================
    // 29. NORMAL FORM LOADING
    // ========================================================

    document
        .querySelectorAll("form")
        .forEach(
            function (form) {

                // Do not interfere with FinPilot AI

                if (
                    form.id ===
                    "finpilot-ai-form"
                ) {
                    return;
                }


                form.addEventListener(
                    "submit",
                    function () {

                        const submitButton =
                            form.querySelector(
                                'button[type="submit"], ' +
                                'input[type="submit"]'
                            );


                        if (!submitButton) {
                            return;
                        }


                        if (
                            form.dataset.noLoading ===
                            "true"
                        ) {
                            return;
                        }


                        submitButton.classList.add(
                            "fp-loading"
                        );


                        if (
                            submitButton.tagName ===
                            "BUTTON"
                        ) {

                            submitButton.innerHTML =
                                "⏳ Processing...";


                            submitButton.disabled =
                                true;

                        } else {

                            submitButton.value =
                                "Processing...";


                            submitButton.disabled =
                                true;
                        }
                    }
                );
            }
        );


    // ========================================================
    // 30. ACCESSIBILITY
    // ========================================================

    if (aiPanel) {

        aiPanel.setAttribute(
            "aria-hidden",
            "true"
        );
    }


    if (aiToggle) {

        aiToggle.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    // ========================================================
    // 31. DEBUG
    // ========================================================

    if (!aiToggle) {

        console.warn(
            "⚠️ FinPilot AI toggle not found."
        );
    }


    if (!aiPanel) {

        console.warn(
            "⚠️ FinPilot AI panel not found."
        );
    }


    if (!aiForm) {

        console.warn(
            "⚠️ FinPilot AI form not found."
        );
    }


    console.log(
        "%cDesigned & Developed by Shabareesh M",
        "color:#4dabff;font-size:16px;font-weight:bold;"
    );


    console.log(
        "🤖 FinPilot Global AI Assistant Ready"
    );

});