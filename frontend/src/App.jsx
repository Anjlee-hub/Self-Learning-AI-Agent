import { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "agent",
      text: "Hello! I'm your Self-Learning AI Agent. Ask me something and I'll process it using my tools, memory, and learned strategies.",
    },
  ]);

  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("Checking backend...");

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        if (response.ok && data.status === "healthy") {
          setBackendStatus(`Backend online${data.ollama_available === false ? " (Ollama unavailable)" : ""}`);
        } else {
          setBackendStatus("Backend responded unexpectedly");
        }
      } catch (error) {
        setBackendStatus("Backend offline");
      }
    };

    checkBackend();
  }, []);

  const sendMessage = async () => {
    const text = message.trim();

    if (!text || loading) {
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text,
      },
    ]);

    setMessage("");
    setLoading(true);
    setActivity([]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Request failed.");
      }

      setActivity(data.activity || []);

      setMessages((previous) => [
        ...previous,
        {
          role: "agent",
          text: data.response,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "agent",
          text: `Error: ${error.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">

      <header className="header">
        <div className="brand">
          <div className="brand-mark">AI</div>

          <div>
            <h1>Self-Learning AI Agent</h1>
            <p>Memory • Tools • Learning • Verification</p>
          </div>
        </div>

        <div className="online-status">
          <span className="status-dot"></span>
          {backendStatus}
        </div>
      </header>

      <section className="hero">
        <div className="hero-badge">
          AUTONOMOUS AI SYSTEM
        </div>

        <h2>
          An AI agent that learns from experience.
        </h2>

        <p>
          Ask a question, give the agent a task, or test one of its tools.
          The agent can retrieve previous lessons, use tools, verify results,
          evaluate its response, and improve future behavior.
        </p>
      </section>

      <main className="main-content">

        <section className="chat-card">

          <div className="chat-header">
            <div>
              <h3>Agent Conversation</h3>
              <p>{backendStatus}</p>
            </div>

            <div className="connection-status">
              <span className="status-dot"></span>
              {backendStatus.includes("offline") ? "Offline" : "Connected"}
            </div>
          </div>

          <div className="messages">

            {messages.map((item, index) => (
              <div
                key={index}
                className={`message-row ${item.role}`}
              >
                <div className="message-label">
                  {item.role === "agent" ? "AI" : "U"}
                </div>

                <div className="message-content">
                  <div className="message-name">
                    {item.role === "agent" ? "Agent" : "You"}
                  </div>

                  <div className="message-bubble">
                    {item.text}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row agent">
                <div className="message-label">
                  AI
                </div>

                <div className="message-content">
                  <div className="message-name">
                    Agent
                  </div>

                  <div className="message-bubble typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

          </div>

          {activity.length > 0 && (
            <div className="activity-panel">

              <div className="activity-header">
                <div className="activity-icon">
                  ⚡
                </div>

                <div>
                  <h4>Agent Activity</h4>
                  <p>High-level execution trace</p>
                </div>
              </div>

              <div className="activity-list">

                {activity.map((step, index) => (
                  <div
                    className="activity-item"
                    key={index}
                  >
                    <span className="activity-check">
                      ✓
                    </span>

                    <span>{step}</span>
                  </div>
                ))}

              </div>
            </div>
          )}

          <div className="input-area">

            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask your AI agent something..."
              disabled={loading}
              rows={1}
            />

            <button
              onClick={sendMessage}
              disabled={loading || !message.trim()}
            >
              {loading ? "Processing..." : "Send"}
            </button>

          </div>

          <div className="input-hint">
            Press Enter to send • Shift + Enter for a new line
          </div>

        </section>

        <section className="capabilities">

          <div className="capability-card">
            <div className="capability-icon">M</div>
            <h4>Memory</h4>
            <p>
              Stores reusable lessons from previous experiences.
            </p>
          </div>

          <div className="capability-card">
            <div className="capability-icon">T</div>
            <h4>Tools</h4>
            <p>
              Uses calculators, time tools, and other operations.
            </p>
          </div>

          <div className="capability-card">
            <div className="capability-icon">V</div>
            <h4>Verification</h4>
            <p>
              Independently checks important tool results.
            </p>
          </div>

          <div className="capability-card">
            <div className="capability-icon">L</div>
            <h4>Learning</h4>
            <p>
              Extracts and retrieves behavioral strategies.
            </p>
          </div>

        </section>

      </main>

      <footer className="footer">
        Self-Learning AI Agent
      </footer>

    </div>
  );
}

export default App;