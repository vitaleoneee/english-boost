(() => {
    const root = document.querySelector("#support-moderator");
    if (!root) {
        return;
    }

    const layout = root.querySelector(".support-moderator__layout");
    const filterButtons = root.querySelectorAll("[data-status]");
    const countElements = root.querySelectorAll("[data-count]");
    const requestList = root.querySelector(".support-moderator__request-list");
    const listStatus = root.querySelector(".support-moderator__list-status");
    const empty = root.querySelector(".support-moderator__empty");
    const queueConnection = root.querySelector(".support-moderator__queue-connection");
    const placeholder = root.querySelector(".support-moderator__placeholder");
    const conversation = root.querySelector(".support-moderator__conversation");
    const requestTitle = root.querySelector(".support-moderator__request-title");
    const username = root.querySelector(".support-moderator__username");
    const chatConnection = root.querySelector(".support-moderator__chat-connection");
    const statusElement = root.querySelector(".support-moderator__status");
    const closeRequestButton = root.querySelector(".support-moderator__close-request");
    const notice = root.querySelector(".support-moderator__notice");
    const messages = root.querySelector(".support-moderator__messages");
    const closedMessage = root.querySelector(".support-moderator__closed");
    const messageForm = root.querySelector(".support-moderator__message-form");
    const messageInput = root.querySelector("#moderator-message");
    const messageSubmit = messageForm.querySelector('button[type="submit"]');
    const mobileBack = root.querySelector(".support-moderator__mobile-back");
    const csrfToken = messageForm.querySelector('[name="csrfmiddlewaretoken"]').value;

    const statusLabels = {
        waiting_moderator: root.dataset.statusWaiting,
        in_progress: root.dataset.statusProgress,
        closed: root.dataset.statusClosed,
    };

    const state = {
        requests: [],
        activeFilter: "",
        currentRequest: null,
        queueSocket: null,
        queueReconnectTimer: null,
        chatSocket: null,
        chatRequestId: null,
        chatReconnectTimer: null,
        chatConnected: false,
    };

    function websocketUrl(path) {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        return `${protocol}://${window.location.host}${path}`;
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
            throw new Error(data.error?.message || root.dataset.loadError);
        }
        return data;
    }

    async function loadRequests() {
        listStatus.textContent = root.dataset.connecting;
        try {
            const response = await fetch(root.dataset.requestsUrl, {
                headers: {Accept: "application/json"},
                credentials: "same-origin",
            });
            const data = await readResponse(response);
            state.requests = data.requests;
            renderCounts();
            renderRequestList();
            listStatus.textContent = "";
        } catch (error) {
            listStatus.textContent = error.message || root.dataset.loadError;
        }
    }

    function renderCounts() {
        const counts = {
            all: state.requests.length,
            waiting_moderator: 0,
            in_progress: 0,
            closed: 0,
        };
        state.requests.forEach((supportRequest) => {
            counts[supportRequest.status] += 1;
        });
        countElements.forEach((element) => {
            element.textContent = counts[element.dataset.count];
        });
    }

    function renderRequestList() {
        const visibleRequests = state.activeFilter
            ? state.requests.filter((item) => item.status === state.activeFilter)
            : state.requests;

        requestList.replaceChildren();
        empty.hidden = visibleRequests.length !== 0;

        visibleRequests.forEach((supportRequest) => {
            const button = document.createElement("button");
            const heading = document.createElement("span");
            const user = document.createElement("strong");
            const requestStatus = document.createElement("span");
            const meta = document.createElement("span");
            const requestNumber = document.createElement("span");
            const createdAt = document.createElement("time");

            button.type = "button";
            button.className = "support-moderator__request-card";
            button.dataset.requestId = supportRequest.id;
            if (supportRequest.id === state.currentRequest?.id) {
                button.classList.add("active");
            }

            heading.className = "support-moderator__card-heading";
            user.textContent = supportRequest.user.username;
            requestStatus.className = "support-moderator__card-status";
            requestStatus.textContent = statusLabels[supportRequest.status]
                || supportRequest.status;
            meta.className = "support-moderator__card-meta";
            requestNumber.textContent = `#${supportRequest.id}`;
            createdAt.dateTime = supportRequest.created_at;
            createdAt.textContent = formatDate(supportRequest.created_at);

            heading.append(user, requestStatus);
            meta.append(requestNumber, createdAt);
            button.append(heading, meta);
            button.addEventListener("click", () => openRequest(supportRequest.id));
            requestList.append(button);
        });
    }

    async function openRequest(requestId) {
        closeChatSocket();
        showNotice("");
        chatConnection.textContent = root.dataset.connecting;

        try {
            const response = await fetch(`${root.dataset.requestsUrl}${requestId}/`, {
                headers: {Accept: "application/json"},
                credentials: "same-origin",
            });
            const data = await readResponse(response);
            state.currentRequest = data.request;
            renderConversation();
            renderRequestList();
            layout.classList.add("chat-open");
            connectChatSocket(requestId);
        } catch (error) {
            showNotice(error.message || root.dataset.loadError);
        }
    }

    function renderConversation() {
        const supportRequest = state.currentRequest;
        placeholder.hidden = true;
        conversation.hidden = false;
        requestTitle.textContent = `#${supportRequest.id}`;
        username.textContent = supportRequest.user.username;
        renderMessages(supportRequest.messages || []);
        updateConversationState(supportRequest);
    }

    function updateConversationState(requestState) {
        state.currentRequest = {...state.currentRequest, ...requestState};
        const status = state.currentRequest.status;
        statusElement.textContent = statusLabels[status] || status;
        closeRequestButton.hidden = status !== "in_progress";
        closedMessage.hidden = status !== "closed";
        messageForm.hidden = status === "closed";
        updateMessageForm();
    }

    function updateMessageForm() {
        const enabled = state.chatConnected
            && Boolean(state.currentRequest?.can_send_messages);
        messageInput.disabled = !enabled;
        messageSubmit.disabled = !enabled;
    }

    function renderMessages(messageItems) {
        messages.replaceChildren();
        messageItems.forEach(appendMessage);
        messages.scrollTop = messages.scrollHeight;
    }

    function appendMessage(message) {
        if (messages.querySelector(`[data-message-id="${message.id}"]`)) {
            return;
        }

        const item = document.createElement("article");
        const author = document.createElement("span");
        const text = document.createElement("p");
        const createdAt = document.createElement("time");

        item.className = `support-moderator__message support-moderator__message--${message.author}`;
        item.dataset.messageId = message.id;
        author.className = "support-moderator__message-author";
        author.textContent = message.author_name;
        text.textContent = message.text;
        createdAt.dateTime = message.created_at;
        createdAt.textContent = formatDate(message.created_at);

        item.append(author, text, createdAt);
        messages.append(item);
        messages.scrollTop = messages.scrollHeight;
    }

    function connectQueueSocket() {
        const socket = new WebSocket(websocketUrl(root.dataset.queueWebsocketPath));
        state.queueSocket = socket;
        queueConnection.textContent = root.dataset.connecting;

        socket.addEventListener("open", () => {
            if (state.queueSocket !== socket) {
                return;
            }
            queueConnection.textContent = root.dataset.connected;
        });

        socket.addEventListener("message", (event) => {
            if (state.queueSocket !== socket) {
                return;
            }
            const data = JSON.parse(event.data);
            if (data.type === "request.created"
                || data.type === "request.status_changed") {
                if (data.request_id === state.currentRequest?.id
                    && data.type === "request.status_changed") {
                    updateConversationState({status: data.status});
                }
                loadRequests();
            }
        });

        socket.addEventListener("close", (event) => {
            if (state.queueSocket !== socket) {
                return;
            }
            queueConnection.textContent = root.dataset.disconnected;
            if (![1000, 4401, 4403].includes(event.code)) {
                state.queueReconnectTimer = window.setTimeout(connectQueueSocket, 2000);
            }
        });
    }

    function connectChatSocket(requestId) {
        state.chatRequestId = requestId;
        const socket = new WebSocket(
            websocketUrl(`${root.dataset.chatWebsocketPath}${requestId}/`),
        );
        state.chatSocket = socket;
        chatConnection.textContent = root.dataset.connecting;

        socket.addEventListener("open", () => {
            if (state.chatSocket !== socket) {
                return;
            }
            state.chatConnected = true;
            chatConnection.textContent = root.dataset.connected;
            updateMessageForm();
        });

        socket.addEventListener("message", (event) => {
            if (state.chatSocket !== socket) {
                return;
            }
            const data = JSON.parse(event.data);
            if (data.type === "request.state") {
                updateConversationState(data);
            } else if (data.type === "message.history") {
                renderMessages(data.messages);
            } else if (data.type === "message.created") {
                appendMessage(data.message);
            } else if (data.type === "request.status_changed") {
                updateConversationState(data);
            } else if (data.type === "error") {
                showNotice(data.message);
            }
        });

        socket.addEventListener("close", (event) => {
            if (state.chatSocket !== socket) {
                return;
            }
            state.chatConnected = false;
            updateMessageForm();
            if (state.chatRequestId !== requestId) {
                return;
            }
            chatConnection.textContent = root.dataset.disconnected;
            if (![1000, 4401, 4403, 4404].includes(event.code)) {
                state.chatReconnectTimer = window.setTimeout(
                    () => connectChatSocket(requestId),
                    2000,
                );
            }
        });
    }

    function closeChatSocket() {
        window.clearTimeout(state.chatReconnectTimer);
        state.chatReconnectTimer = null;
        state.chatRequestId = null;
        state.chatConnected = false;
        if (state.chatSocket) {
            const socket = state.chatSocket;
            state.chatSocket = null;
            socket.close(1000);
        }
    }

    function showNotice(message) {
        notice.textContent = message;
        notice.hidden = !message;
    }

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            state.activeFilter = button.dataset.status;
            filterButtons.forEach((item) => item.classList.toggle("active", item === button));
            renderRequestList();
        });
    });

    messageForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = messageInput.value.trim();
        if (!text || state.chatSocket?.readyState !== WebSocket.OPEN) {
            return;
        }
        state.chatSocket.send(JSON.stringify({type: "message.send", text}));
        messageInput.value = "";
    });

    closeRequestButton.addEventListener("click", async () => {
        if (!state.currentRequest) {
            return;
        }
        closeRequestButton.disabled = true;
        try {
            const response = await fetch(
                `${root.dataset.requestsUrl}${state.currentRequest.id}/close/`,
                {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    credentials: "same-origin",
                },
            );
            const data = await readResponse(response);
            updateConversationState(data.request);
        } catch (error) {
            showNotice(error.message || root.dataset.sendError);
        } finally {
            closeRequestButton.disabled = false;
        }
    });

    mobileBack.addEventListener("click", () => {
        layout.classList.remove("chat-open");
        closeChatSocket();
    });

    window.addEventListener("beforeunload", () => {
        window.clearTimeout(state.queueReconnectTimer);
        closeChatSocket();
        if (state.queueSocket) {
            state.queueSocket.close(1000);
        }
    });

    loadRequests();
    connectQueueSocket();
})();
