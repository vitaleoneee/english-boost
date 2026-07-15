(() => {
    const widget = document.querySelector("#support-widget");
    if (!widget) {
        return;
    }

    const launcher = widget.querySelector(".support-widget__launcher");
    const panel = widget.querySelector(".support-widget__panel");
    const closeButton = widget.querySelector(".support-widget__close");
    const backButton = widget.querySelector(".support-widget__back");
    const title = widget.querySelector(".support-widget__title");
    const notice = widget.querySelector(".support-widget__notice");
    const screens = widget.querySelectorAll("[data-screen]");
    const listScreen = widget.querySelector('[data-screen="list"]');
    const requestList = widget.querySelector(".support-widget__request-list");
    const loading = widget.querySelector(".support-widget__loading");
    const empty = widget.querySelector(".support-widget__empty");
    const newButton = widget.querySelector(".support-widget__new-button");
    const newForm = widget.querySelector(".support-widget__new-form");
    const newMessage = widget.querySelector("#support-new-message");
    const messages = widget.querySelector(".support-widget__messages");
    const statusBadge = widget.querySelector(".support-widget__status-badge");
    const connection = widget.querySelector(".support-widget__connection");
    const waiting = widget.querySelector(".support-widget__waiting");
    const rating = widget.querySelector(".support-widget__rating");
    const rated = widget.querySelector(".support-widget__rated");
    const messageForm = widget.querySelector(".support-widget__message-form");
    const messageInput = widget.querySelector("#support-chat-message");
    const messageSubmit = messageForm.querySelector('button[type="submit"]');
    const csrfToken = newForm.querySelector('[name="csrfmiddlewaretoken"]').value;

    const state = {
        currentRequest: null,
        socket: null,
        socketRequestId: null,
        reconnectTimer: null,
        socketConnected: false,
        canSendMessages: false,
    };

    const statusLabels = {
        waiting_moderator: widget.dataset.statusWaiting,
        in_progress: widget.dataset.statusProgress,
        closed: widget.dataset.statusClosed,
    };

    function showNotice(message) {
        notice.textContent = message;
        notice.hidden = !message;
    }

    function showScreen(name) {
        screens.forEach((screen) => {
            screen.hidden = screen.dataset.screen !== name;
        });
        backButton.hidden = name === "list";
        title.textContent = name === "chat" && state.currentRequest
            ? `${widget.dataset.requestLabel} #${state.currentRequest.id}`
            : launcher.querySelector("span").textContent;
        showNotice("");
    }

    function setPanelOpen(isOpen) {
        panel.hidden = !isOpen;
        launcher.setAttribute("aria-expanded", String(isOpen));
        if (isOpen) {
            showRequestList();
        } else {
            closeSocket();
        }
    }

    function formatDate(value) {
        return new Intl.DateTimeFormat(document.documentElement.lang || undefined, {
            dateStyle: "short",
            timeStyle: "short",
        }).format(new Date(value));
    }

    async function readResponse(response) {
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error?.message || widget.dataset.loadError);
        }
        return data;
    }

    async function showRequestList() {
        closeSocket();
        state.currentRequest = null;
        showScreen("list");
        requestList.replaceChildren();
        empty.hidden = true;
        loading.hidden = false;

        try {
            const response = await fetch(widget.dataset.requestsUrl, {
                headers: {Accept: "application/json"},
                credentials: "same-origin",
            });
            const data = await readResponse(response);
            renderRequestList(data.requests);
        } catch (error) {
            showNotice(error.message || widget.dataset.loadError);
        } finally {
            loading.hidden = true;
        }
    }

    function renderRequestList(requests) {
        requestList.replaceChildren();
        empty.hidden = requests.length !== 0;

        requests.forEach((supportRequest) => {
            const button = document.createElement("button");
            const heading = document.createElement("span");
            const requestName = document.createElement("span");
            const requestStatus = document.createElement("span");
            const createdAt = document.createElement("time");

            button.type = "button";
            button.className = "support-widget__request";
            heading.className = "support-widget__request-heading";
            requestStatus.className = "support-widget__request-status";
            requestName.textContent = `${widget.dataset.requestLabel} #${supportRequest.id}`;
            requestStatus.textContent = statusLabels[supportRequest.status] || supportRequest.status;
            createdAt.dateTime = supportRequest.created_at;
            createdAt.textContent = formatDate(supportRequest.created_at);

            heading.append(requestName, requestStatus);
            button.append(heading, createdAt);
            button.addEventListener("click", () => openChat(supportRequest.id));
            requestList.append(button);
        });
    }

    async function openChat(requestId) {
        closeSocket();
        showScreen("chat");
        messages.replaceChildren();
        connection.textContent = widget.dataset.connectionConnecting;

        try {
            const response = await fetch(`${widget.dataset.requestsUrl}${requestId}/`, {
                headers: {Accept: "application/json"},
                credentials: "same-origin",
            });
            const data = await readResponse(response);
            state.currentRequest = data.request;
            title.textContent = `${widget.dataset.requestLabel} #${data.request.id}`;
            renderMessages(data.request.messages);
            updateRequestState(data.request);
            connectSocket(requestId);
        } catch (error) {
            showNotice(error.message || widget.dataset.loadError);
            connection.textContent = "";
        }
    }

    function renderMessages(messageItems) {
        messages.replaceChildren();
        messageItems.forEach(appendMessage);
        scrollMessagesToBottom();
    }

    function appendMessage(message) {
        if (messages.querySelector(`[data-message-id="${message.id}"]`)) {
            return;
        }

        const item = document.createElement("article");
        const author = document.createElement("span");
        const text = document.createElement("p");
        const createdAt = document.createElement("time");

        item.className = `support-widget__message support-widget__message--${message.author}`;
        item.dataset.messageId = message.id;
        author.className = "support-widget__message-author";
        author.textContent = message.author_name;
        text.textContent = message.text;
        createdAt.dateTime = message.created_at;
        createdAt.textContent = formatDate(message.created_at);

        item.append(author, text, createdAt);
        messages.append(item);
        scrollMessagesToBottom();
    }

    function scrollMessagesToBottom() {
        messages.scrollTop = messages.scrollHeight;
    }

    function updateRequestState(requestState) {
        state.currentRequest = {...state.currentRequest, ...requestState};
        state.canSendMessages = Boolean(state.currentRequest.can_send_messages);
        statusBadge.textContent = statusLabels[state.currentRequest.status]
            || state.currentRequest.status;
        waiting.hidden = state.currentRequest.status !== "waiting_moderator";
        rating.hidden = !state.currentRequest.can_rate;
        rated.hidden = state.currentRequest.status !== "closed"
            || !state.currentRequest.rating;
        updateMessageForm();
    }

    function updateMessageForm() {
        const enabled = state.socketConnected && state.canSendMessages;
        messageInput.disabled = !enabled;
        messageSubmit.disabled = !enabled;
        messageForm.hidden = state.currentRequest?.status === "closed";
    }

    function connectSocket(requestId) {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const socketUrl = `${protocol}://${window.location.host}${widget.dataset.websocketPath}${requestId}/`;

        state.socketRequestId = requestId;
        const socket = new WebSocket(socketUrl);
        state.socket = socket;
        connection.textContent = widget.dataset.connectionConnecting;

        socket.addEventListener("open", () => {
            if (state.socket !== socket) {
                return;
            }
            state.socketConnected = true;
            connection.textContent = widget.dataset.connectionConnected;
            updateMessageForm();
        });

        socket.addEventListener("message", (event) => {
            if (state.socket !== socket) {
                return;
            }
            const data = JSON.parse(event.data);

            if (data.type === "request.state") {
                updateRequestState(data);
            } else if (data.type === "message.history") {
                renderMessages(data.messages);
            } else if (data.type === "message.created") {
                appendMessage(data.message);
            } else if (data.type === "request.status_changed") {
                updateRequestState(data);
            } else if (data.type === "error") {
                showNotice(data.message);
            }
        });

        socket.addEventListener("close", (event) => {
            if (state.socket !== socket) {
                return;
            }
            state.socketConnected = false;
            updateMessageForm();

            if (state.socketRequestId !== requestId) {
                return;
            }

            connection.textContent = widget.dataset.connectionDisconnected;
            if (![1000, 4401, 4403, 4404].includes(event.code) && !panel.hidden) {
                state.reconnectTimer = window.setTimeout(
                    () => connectSocket(requestId),
                    2000,
                );
            }
        });
    }

    function closeSocket() {
        window.clearTimeout(state.reconnectTimer);
        state.reconnectTimer = null;
        state.socketRequestId = null;
        state.socketConnected = false;

        if (state.socket) {
            const socket = state.socket;
            state.socket = null;
            socket.close(1000);
        }
    }

    launcher.addEventListener("click", () => setPanelOpen(panel.hidden));
    closeButton.addEventListener("click", () => setPanelOpen(false));
    backButton.addEventListener("click", showRequestList);
    newButton.addEventListener("click", () => {
        showScreen("new");
        newMessage.focus();
    });

    newForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const submitButton = newForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            const response = await fetch(widget.dataset.requestsUrl, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                credentials: "same-origin",
                body: JSON.stringify({text: newMessage.value}),
            });
            const data = await readResponse(response);
            newForm.reset();
            await openChat(data.request.id);
        } catch (error) {
            showNotice(error.message || widget.dataset.sendError);
        } finally {
            submitButton.disabled = false;
        }
    });

    messageForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = messageInput.value.trim();
        if (!text || state.socket?.readyState !== WebSocket.OPEN) {
            return;
        }

        state.socket.send(JSON.stringify({type: "message.send", text}));
        messageInput.value = "";
    });

    rating.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-helped]");
        if (!button || !state.currentRequest) {
            return;
        }

        rating.querySelectorAll("button").forEach((item) => {
            item.disabled = true;
        });

        try {
            const response = await fetch(
                `${widget.dataset.requestsUrl}${state.currentRequest.id}/rating/`,
                {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    credentials: "same-origin",
                    body: JSON.stringify({helped: button.dataset.helped === "true"}),
                },
            );
            const data = await readResponse(response);
            updateRequestState({
                can_rate: false,
                rating: {helped: data.rating.helped},
            });
        } catch (error) {
            showNotice(error.message || widget.dataset.sendError);
            rating.querySelectorAll("button").forEach((item) => {
                item.disabled = false;
            });
        }
    });
})();
