import { useState } from "react";

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

function App() {
  const [studentIdDraft, setStudentIdDraft] = useState("");
  const [playgroundDraft, setPlaygroundDraft] = useState("");
  const [sessionIdDraft, setSessionIdDraft] = useState("");
  const [studentId, setStudentId] = useState("");
  const [playground, setPlayground] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState(starterMessages);
  const [pendingAction, setPendingAction] = useState("");
  const [reviewDrafts, setReviewDrafts] = useState({});
  const [openReviews, setOpenReviews] = useState({});
  const [pendingFeedback, setPendingFeedback] = useState({});
  const apiBase = defaultApiBase;

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
    const trimmedPlayground = playgroundDraft.trim();
    const trimmedSessionId = sessionIdDraft.trim();
    if (!trimmedStudentId || !trimmedPlayground || !trimmedSessionId) {
      return;
    }
    setStudentId(trimmedStudentId);
    setPlayground(trimmedPlayground);
    setSessionId(trimmedSessionId);
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
      const messageResponse = await postJson(`/students/${studentId}/messages`, {
        session_id: sessionId,
        message: trimmedDraft,
        playground,
      });
      const responseRecord = await postJson(`/students/${studentId}/responses`, {
        message_id: messageResponse.message_id,
        session_id: sessionId,
        playground,
        student_message: trimmedDraft,
      });
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
    setPendingAction("help");

    try {
      const messageResponse = await postJson(`/students/${studentId}/messages`, {
        session_id: sessionId,
        message: "",
        playground,
      });
      const responseRecord = await postJson(`/students/${studentId}/responses`, {
        message_id: messageResponse.message_id,
        session_id: sessionId,
        playground,
        student_message: "Help",
      });
      appendMessage({
        id: responseRecord.response_id,
        role: "assistant",
        body: responseRecord.response_text,
        meta: responseRecord.llm_model || "Generated response",
        canFeedback: true,
      });
    } catch (error) {
      appendMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        body: "Help could not be sent right now.",
        meta: `Failed to send: ${error.message}`,
      });
    } finally {
      setPendingAction("");
    }
  };

  if (!studentId) {
    return (
      <main className="app-shell">
        <section className="start-card">
          <h1>Start Chat</h1>
          <p>Enter your student ID, playground, and session ID before starting the chat.</p>
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
            <label className="sr-only" htmlFor="playground">
              Playground
            </label>
            <input
              id="playground"
              type="text"
              value={playgroundDraft}
              onChange={(event) => setPlaygroundDraft(event.target.value)}
              placeholder="Playground"
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
              placeholder="Session ID (UUID)"
              autoComplete="off"
            />
            <button type="submit">Start Chat</button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <section className="chat-card">
        <header className="toolbar">
          <div className="toolbar-copy">
            <h1>Chat</h1>
            <p>{studentId} · {playground} · {sessionId}</p>
          </div>
          <button
            type="button"
            className="help-button"
            onClick={handleHelp}
            disabled={pendingAction === "help"}
          >
            {pendingAction === "help" ? "Sending..." : "Help"}
          </button>
        </header>

        <div className="workspace">
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
                  <p>{message.body}</p>
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
      </section>
    </main>
  );
}

export default App;
