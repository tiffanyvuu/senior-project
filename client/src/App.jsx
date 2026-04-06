import { useEffect, useRef, useState } from "react";

const defaultApiBase = "http://127.0.0.1:8000/v1";

const starterMessages = [
  {
    id: "assistant-intro",
    role: "assistant",
    body:
      "Hi! I am your coding helper. Ask a question about your project, or tap 'Help' for assistance.",
    meta: "Ready to help",
    canFeedback: false,
  },
];

function renderInlineMarkdown(text) {
  const parts = [];
  const pattern = /(\*\*[^*]+\*\*|__[^_]+__|`[^`]+`)/g;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    const token = match[0];
    if (token.startsWith("**") || token.startsWith("__")) {
      parts.push(<strong key={`${match.index}-strong`}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("`")) {
      parts.push(<code key={`${match.index}-code`}>{token.slice(1, -1)}</code>);
    }

    lastIndex = match.index + token.length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts;
}

function renderMessageBody(text) {
  if (typeof text !== "string") {
    return text;
  }

  const lines = text.split("\n");
  const elements = [];
  let listItems = [];
  let listType = null;

  const flushList = (key) => {
    if (!listItems.length) {
      return;
    }

    const Tag = listType === "ol" ? "ol" : "ul";
    elements.push(<Tag key={key} className="message-list-block">{listItems}</Tag>);
    listItems = [];
    listType = null;
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    const unorderedMatch = trimmed.match(/^[-*]\s+(.*)$/);
    const orderedMatch = trimmed.match(/^\d+\.\s+(.*)$/);

    if (!trimmed) {
      flushList(`list-${index}`);
      return;
    }

    if (unorderedMatch) {
      if (listType && listType !== "ul") {
        flushList(`list-${index}`);
      }
      listType = "ul";
      listItems.push(
        <li key={`li-${index}`}>{renderInlineMarkdown(unorderedMatch[1])}</li>,
      );
      return;
    }

    if (orderedMatch) {
      if (listType && listType !== "ol") {
        flushList(`list-${index}`);
      }
      listType = "ol";
      listItems.push(
        <li key={`li-${index}`}>{renderInlineMarkdown(orderedMatch[1])}</li>,
      );
      return;
    }

    flushList(`list-${index}`);
    elements.push(
      <p key={`p-${index}`} className="message-body">
        {renderInlineMarkdown(line)}
      </p>,
    );
  });

  flushList("list-final");
  return elements;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function getDefaultPanelRect() {
  const width = 460;
  const height = 760;
  return {
    x: Math.max(12, window.innerWidth - width - 24),
    y: 32,
    width,
    height,
  };
}

function App() {
  const [studentIdDraft, setStudentIdDraft] = useState("");
  const [sessionIdDraft, setSessionIdDraft] = useState("");
  const [studentId, setStudentId] = useState("");
  const [sessionId, setSessionId] = useState("Detecting latest session");
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState(starterMessages);
  const [pendingAction, setPendingAction] = useState("");
  const [reviewDrafts, setReviewDrafts] = useState({});
  const [openReviews, setOpenReviews] = useState({});
  const [pendingFeedback, setPendingFeedback] = useState({});
  const [panelRect, setPanelRect] = useState(getDefaultPanelRect);
  const [isChatOpen, setIsChatOpen] = useState(true);
  const interactionRef = useRef(null);
  const apiBase = defaultApiBase;

  useEffect(() => {
    const handlePointerMove = (event) => {
      const interaction = interactionRef.current;
      if (!interaction) {
        return;
      }

      if (interaction.type === "drag") {
        setPanelRect((current) => {
          const nextX = clamp(
            event.clientX - interaction.offsetX,
            12,
            window.innerWidth - current.width - 12,
          );
          const nextY = clamp(
            event.clientY - interaction.offsetY,
            12,
            window.innerHeight - 120,
          );
          return {
            ...current,
            x: nextX,
            y: nextY,
          };
        });
        return;
      }

      if (interaction.type === "resize") {
        const nextRight = event.clientX + interaction.cornerOffsetX;
        const nextBottom = event.clientY + interaction.cornerOffsetY;
        const nextWidth = clamp(
          nextRight - interaction.startRect.x,
          360,
          window.innerWidth - interaction.startRect.x - 12,
        );
        const nextHeight = clamp(
          nextBottom - interaction.startRect.y,
          520,
          window.innerHeight - interaction.startRect.y - 12,
        );
        setPanelRect((current) => ({
          ...current,
          width: nextWidth,
          height: nextHeight,
        }));
      }
    };

    const handlePointerUp = () => {
      interactionRef.current = null;
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, []);

  const startDrag = (event) => {
    if (event.target.closest("button, textarea, input")) {
      return;
    }
    interactionRef.current = {
      type: "drag",
      offsetX: event.clientX - panelRect.x,
      offsetY: event.clientY - panelRect.y,
    };
  };

  const startResize = (event) => {
    event.preventDefault();
    event.stopPropagation();
    const cornerX = panelRect.x + panelRect.width;
    const cornerY = panelRect.y + panelRect.height;
    interactionRef.current = {
      type: "resize",
      cornerOffsetX: cornerX - event.clientX,
      cornerOffsetY: cornerY - event.clientY,
      startRect: { ...panelRect },
    };
  };

  const appendMessage = (message) => {
    setMessages((current) => [...current, message]);
  };

  const postJson = async (path, payload) => {
    const response = await fetch(`${apiBase}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.detail || `Request failed with status ${response.status}`);
    }

    return data;
  };

  const updateMessage = (messageId, updater) => {
    setMessages((current) =>
      current.map((message) =>
        message.id === messageId ? updater(message) : message,
      ),
    );
  };

  const handleFeedback = async (responseId, thumb) => {
    setPendingFeedback((current) => ({ ...current, [responseId]: thumb }));

    try {
      const comment = (reviewDrafts[responseId] || "").trim();
      await postJson(`/students/${studentId}/responses/${responseId}/feedback`, {
        thumb,
        comment: comment || null,
      });
      updateMessage(responseId, (message) => ({
        ...message,
        feedbackStatus: thumb === "up" ? "Thanks for the thumbs up." : "Thanks for the feedback.",
        selectedThumb: thumb,
      }));
    } catch (error) {
      updateMessage(responseId, (message) => ({
        ...message,
        feedbackStatus: `Feedback failed: ${error.message}`,
      }));
    } finally {
      setPendingFeedback((current) => {
        const next = { ...current };
        delete next[responseId];
        return next;
      });
    }
  };

  const handleReviewSubmit = async (responseId) => {
    const selectedThumb = messages.find((message) => message.id === responseId)?.selectedThumb;

    if (!selectedThumb) {
      updateMessage(responseId, (message) => ({
        ...message,
        feedbackStatus: "Choose thumbs up or thumbs down first.",
      }));
      return;
    }

    setPendingFeedback((current) => ({ ...current, [responseId]: "review" }));

    try {
      const comment = (reviewDrafts[responseId] || "").trim();
      await postJson(`/students/${studentId}/responses/${responseId}/feedback`, {
        thumb: selectedThumb,
        comment: comment || null,
      });
      updateMessage(responseId, (message) => ({
        ...message,
        feedbackStatus: "Review sent.",
      }));
      setOpenReviews((current) => ({ ...current, [responseId]: false }));
    } catch (error) {
      updateMessage(responseId, (message) => ({
        ...message,
        feedbackStatus: `Review failed: ${error.message}`,
      }));
    } finally {
      setPendingFeedback((current) => {
        const next = { ...current };
        delete next[responseId];
        return next;
      });
    }
  };

  const handleStudentStart = (event) => {
    event.preventDefault();
    const trimmedStudentId = studentIdDraft.trim();
    const trimmedSessionId = sessionIdDraft.trim();
    if (!trimmedStudentId) {
      return;
    }
    setStudentId(trimmedStudentId);
    setSessionId(trimmedSessionId || "Detecting latest session");
  };

  const handleSend = async (event) => {
    event.preventDefault();

    const trimmedDraft = draft.trim();
    if (!trimmedDraft) {
      return;
    }

    const optimisticMessage = {
      id: crypto.randomUUID(),
      role: "student",
      body: trimmedDraft,
      meta: "Sending",
    };

    appendMessage(optimisticMessage);
    setDraft("");
    setPendingAction("message");

    try {
      const messagePayload = {
        message: trimmedDraft,
        ...(sessionIdDraft.trim() ? { session_id: sessionIdDraft.trim() } : {}),
      };
      const messageResponse = await postJson(`/students/${studentId}/messages`, messagePayload);
      setSessionId(messageResponse.session_id);
      const responseRecord = await postJson(`/students/${studentId}/responses`, {
        message_id: messageResponse.message_id,
        session_id: messageResponse.session_id,
        student_message: trimmedDraft,
      });
      setSessionId(responseRecord.session_id);
      setMessages((current) =>
        [
          ...current.map((message) =>
            message.id === optimisticMessage.id
              ? {
                  ...message,
                  meta: "Sent",
                }
              : message,
          ),
          {
            id: responseRecord.response_id,
            role: "assistant",
            body: responseRecord.response_text,
            meta: responseRecord.llm_model || "Generated response",
            canFeedback: true,
          },
        ],
      );
    } catch (error) {
      setMessages((current) =>
        current.map((message) =>
          message.id === optimisticMessage.id
            ? {
                ...message,
                meta: `Failed to send: ${error.message}`,
              }
            : message,
        ),
      );
    } finally {
      setPendingAction("");
    }
  };

  const handleHelp = async () => {
    const helpMessage = {
      id: crypto.randomUUID(),
      role: "student",
      body: "Help",
      meta: "Sending",
    };

    appendMessage(helpMessage);
    setPendingAction("help");

    try {
      const messagePayload = {
        message: "",
        ...(sessionIdDraft.trim() ? { session_id: sessionIdDraft.trim() } : {}),
      };
      const messageResponse = await postJson(`/students/${studentId}/messages`, messagePayload);
      setSessionId(messageResponse.session_id);
      const responseRecord = await postJson(`/students/${studentId}/responses`, {
        message_id: messageResponse.message_id,
        session_id: messageResponse.session_id,
        student_message: "Help",
      });
      setSessionId(responseRecord.session_id);
      setMessages((current) =>
        [
          ...current.map((message) =>
            message.id === helpMessage.id
              ? {
                  ...message,
                  meta: "Sent",
                }
              : message,
          ),
          {
            id: responseRecord.response_id,
            role: "assistant",
            body: responseRecord.response_text,
            meta: responseRecord.llm_model || "Generated response",
            canFeedback: true,
          },
        ],
      );
    } catch (error) {
      setMessages((current) =>
        [
          ...current.map((message) =>
            message.id === helpMessage.id
              ? {
                  ...message,
                  meta: `Failed to send: ${error.message}`,
                }
              : message,
          ),
          {
            id: crypto.randomUUID(),
            role: "assistant",
            body: "Help could not be sent right now.",
            meta: `Failed to send: ${error.message}`,
          },
        ],
      );
    } finally {
      setPendingAction("");
    }
  };

  if (!studentId) {
    return (
      <main className="app-shell">
        <section className="start-card">
          <h1>Start Chat</h1>
          <p>Enter your student ID. Session ID is optional if you want to target a specific test session.</p>
          <form className="start-form" onSubmit={handleStudentStart}>
            <label className="sr-only" htmlFor="student-id">
              Student ID
            </label>
            <input
              id="student-id"
              type="text"
              value={studentIdDraft}
              onChange={(event) => setStudentIdDraft(event.target.value)}
              placeholder="Student ID"
              autoComplete="off"
            />
            <label className="sr-only" htmlFor="session-id">
              Session ID
            </label>
            <input
              id="session-id"
              type="text"
              value={sessionIdDraft}
              onChange={(event) => setSessionIdDraft(event.target.value)}
              placeholder="Session ID (optional)"
              autoComplete="off"
            />
            <button type="submit">Start Chat</button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="overlay-shell">
      <iframe
        className="background-frame"
        src="https://research-vr.vex.com/"
        title="Research VR"
      />

      {isChatOpen ? (
        <section
          className="chat-overlay"
          style={{
            left: `${panelRect.x}px`,
            top: `${panelRect.y}px`,
            width: `${panelRect.width}px`,
            height: `${panelRect.height}px`,
          }}
        >
          <header className="toolbar draggable-toolbar" onPointerDown={startDrag}>
            <div className="toolbar-copy">
              <h1>Chat</h1>
              <p>{studentId} · GO-Mars · {sessionId}</p>
            </div>
            <div className="toolbar-actions">
              <button
                type="button"
                className="help-button"
                onClick={handleHelp}
                disabled={pendingAction === "help"}
              >
                {pendingAction === "help" ? "Sending..." : "Help"}
              </button>
            </div>
          </header>

        <div className="workspace workspace-overlay">
          <section className="message-list" aria-label="Conversation">
            {messages.map((message) => (
              <article
                key={message.id}
                className={`message-row ${message.role === "student" ? "outgoing" : "incoming"}`}
              >
                <div className="message-bubble">
                  <div className="message-label">
                    {message.role === "student" ? "You" : "Agent"}
                  </div>
                  <div className="message-body-wrap">{renderMessageBody(message.body)}</div>
                  <span className="message-meta">{message.meta}</span>
                  {message.role === "assistant" && message.canFeedback ? (
                    <div className="feedback-panel">
                      <div className="feedback-actions">
                        <button
                          type="button"
                          className={`icon-button ${message.selectedThumb === "up" ? "selected" : ""}`}
                          onClick={() => handleFeedback(message.id, "up")}
                          disabled={Boolean(pendingFeedback[message.id])}
                          aria-label="Thumbs up"
                          title="Thumbs up"
                        >
                          {pendingFeedback[message.id] === "up" ? (
                            "..."
                          ) : (
                            <svg viewBox="0 0 24 24" aria-hidden="true">
                              <path d="M10 21H6a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h4v11Zm2-11 2.6-6.1A1.5 1.5 0 0 1 16 3a2 2 0 0 1 2 2v4h2.7a2 2 0 0 1 2 2.4l-1.2 6A2 2 0 0 1 19.5 19H12V10Z" />
                            </svg>
                          )}
                        </button>
                        <button
                          type="button"
                          className={`icon-button ${message.selectedThumb === "down" ? "selected" : ""}`}
                          onClick={() => handleFeedback(message.id, "down")}
                          disabled={Boolean(pendingFeedback[message.id])}
                          aria-label="Thumbs down"
                          title="Thumbs down"
                        >
                          {pendingFeedback[message.id] === "down" ? (
                            "..."
                          ) : (
                            <svg viewBox="0 0 24 24" aria-hidden="true">
                              <path d="M14 3h4a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-4V3Zm-2 11-2.6 6.1A1.5 1.5 0 0 1 8 21a2 2 0 0 1-2-2v-4H3.3a2 2 0 0 1-2-2.4l1.2-6A2 2 0 0 1 4.5 5H12v9Z" />
                            </svg>
                          )}
                        </button>
                        <button
                          type="button"
                          className="review-toggle"
                          onClick={() =>
                            setOpenReviews((current) => ({
                              ...current,
                              [message.id]: !current[message.id],
                            }))
                          }
                        >
                          {openReviews[message.id] ? "Hide Review" : "Add Review"}
                        </button>
                      </div>
                      {openReviews[message.id] ? (
                        <div className="review-form">
                          <textarea
                            rows="2"
                            value={reviewDrafts[message.id] || ""}
                            onChange={(event) =>
                              setReviewDrafts((current) => ({
                                ...current,
                                [message.id]: event.target.value,
                              }))
                            }
                            placeholder="Write a review if you want."
                          />
                          <button
                            type="button"
                            className="send-review"
                            onClick={() => handleReviewSubmit(message.id)}
                            disabled={Boolean(pendingFeedback[message.id])}
                          >
                            {pendingFeedback[message.id] === "review" ? "Sending..." : "Send Review"}
                          </button>
                        </div>
                      ) : null}
                      {message.feedbackStatus ? (
                        <div className="feedback-status">{message.feedbackStatus}</div>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              </article>
            ))}
          </section>
        </div>

        <form className="composer" onSubmit={handleSend}>
          <label className="sr-only" htmlFor="student-message">
            Message
          </label>
          <textarea
            id="student-message"
            rows="3"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Ask about your program, your bug, or what to try next."
          />
          <div className="composer-footer">
            <button type="submit" disabled={pendingAction === "message"}>
              {pendingAction === "message" ? "Sending..." : "Send"}
            </button>
          </div>
        </form>
          <button
            type="button"
            className="resize-handle"
            onPointerDown={startResize}
            aria-label="Resize chat"
            title="Resize chat"
          />
        </section>
      ) : null}

      <button
        type="button"
        className="chat-launcher"
        onClick={() => setIsChatOpen((current) => !current)}
      >
        {isChatOpen ? "Hide Chat" : "Open Chat"}
      </button>
    </main>
  );
}

export default App;
