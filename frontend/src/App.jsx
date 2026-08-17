import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  const [documentData, setDocumentData] = useState(null);

  const [uploading, setUploading] = useState(false);

  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  const [flashcards, setFlashcards] = useState([]);
  const [currentCard, setCurrentCard] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loadingFlashcards, setLoadingFlashcards] = useState(false);

  const [conceptGraph, setConceptGraph] = useState(null);
  const [loadingConcepts, setLoadingConcepts] = useState(false);

  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loadingTutor, setLoadingTutor] = useState(false);

  // ============================================================
  // File Selection
  // ============================================================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);

    setDocumentId(null);
    setDocumentData(null);
    setSummary(null);
    setFlashcards([]);
    setCurrentCard(0);
    setShowAnswer(false);
    setConceptGraph(null);
    setMessages([]);
  };

  // ============================================================
  // Document Upload
  // ============================================================

  const handleUpload = async () => {
    if (!file || uploading) {
      return;
    }

    console.log("PROCESS BUTTON CLICKED");
    console.log("Uploading file:", file.name);

    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      console.log("Upload HTTP status:", response.status);

      if (!response.ok) {
        const errorText = await response.text();

        console.error("Upload failed:", errorText);

        throw new Error(
          `Upload failed with status ${response.status}`
        );
      }

      const data = await response.json();

      console.log("UPLOAD RESPONSE:", data);
      console.log("DOCUMENT ID:", data.document_id);

      if (!data.document_id) {
        throw new Error(
          "Upload succeeded but no document_id was returned."
        );
      }

      const newDocumentId = Number(data.document_id);

      setDocumentData(data);
      setDocumentId(newDocumentId);

      console.log(
        "Dashboard should now open for document:",
        newDocumentId
      );
    } catch (error) {
      console.error("Upload error:", error);

      alert(
        `Unable to process the document.\n\n${error.message}`
      );
    } finally {
      setUploading(false);
    }
  };

  // ============================================================
  // Get Summary
  // ============================================================

  const handleViewSummary = async () => {
    if (!documentId) {
      return;
    }

    setLoadingSummary(true);

    try {
      const response = await fetch(
        `${API_URL}/documents/${documentId}/artifacts`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to fetch document artifacts"
        );
      }

      const data = await response.json();

      console.log("Artifacts:", data);

      setSummary(
        data.artifacts?.summary ||
          "No summary available."
      );
    } catch (error) {
      console.error(error);

      alert("Unable to load the summary.");
    } finally {
      setLoadingSummary(false);
    }
  };

  // ============================================================
  // Get Flashcards
  // ============================================================

  const handlePractice = async () => {
    if (!documentId) {
      return;
    }

    setLoadingFlashcards(true);

    try {
      const response = await fetch(
        `${API_URL}/documents/${documentId}/artifacts`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to fetch flashcards"
        );
      }

      const data = await response.json();

      console.log("Flashcards:", data);

      const cards =
        data.artifacts?.flashcards || [];

      setFlashcards(cards);
      setCurrentCard(0);
      setShowAnswer(false);
    } catch (error) {
      console.error(error);

      alert("Unable to load flashcards.");
    } finally {
      setLoadingFlashcards(false);
    }
  };

  // ============================================================
  // Concept Graph
  // ============================================================

  const handleExploreConcepts = async () => {
    if (!documentId || loadingConcepts) {
      return;
    }

    setLoadingConcepts(true);

    try {
      const response = await fetch(
        `${API_URL}/documents/${documentId}/concept-graph`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to fetch concept graph."
        );
      }

      const data = await response.json();

      console.log("Concept Graph:", data);

      setConceptGraph(data);
    } catch (error) {
      console.error(
        "Concept graph error:",
        error
      );

      alert("Unable to load concepts.");
    } finally {
      setLoadingConcepts(false);
    }
  };

  // ============================================================
  // AI Tutor
  // ============================================================

  const handleAskTutor = async () => {
    const trimmedQuestion =
      question.trim();

    if (
      !trimmedQuestion ||
      !documentId ||
      loadingTutor
    ) {
      return;
    }

    const userMessage = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");
    setLoadingTutor(true);

    try {
      const response = await fetch(
        `${API_URL}/documents/${documentId}/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            question: trimmedQuestion,
            session_id: 1,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to get AI tutor response."
        );
      }

      const data = await response.json();

      console.log(
        "Tutor response:",
        data
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            data.answer ||
            "I couldn't find an answer.",
          sources:
            data.sources || [],
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't answer that question. Please try again.",
          sources: [],
        },
      ]);
    } finally {
      setLoadingTutor(false);
    }
  };

  // ============================================================
  // Enter Key
  // ============================================================

  const handleTutorKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      handleAskTutor();
    }
  };

  // ============================================================
  // Dashboard
  // ============================================================

  if (documentId) {
    return (
      <div className="dashboard">

        <header className="dashboard-navbar">

          <div className="logo">
            Learning<span>AI</span>
          </div>

          <div className="document-name">
            {file?.name}
          </div>

        </header>

        <main className="dashboard-content">

          <div className="dashboard-heading">

            <p className="eyebrow">
              YOUR LEARNING SPACE
            </p>

            <h1>
              Let's learn from your
              <span> document.</span>
            </h1>

            <p>
              Your document has been processed.
              Explore your learning material or
              ask the AI tutor a question.
            </p>

          </div>

          {/* ==================================================
              FEATURE CARDS
              ================================================== */}

          <div className="dashboard-grid">

            {/* Summary */}

            <div className="dashboard-card">

              <div className="card-icon">
                ✦
              </div>

              <h2>
                Summary
              </h2>

              <p>
                Review the key ideas and important
                information from your document.
              </p>

              <button
                onClick={handleViewSummary}
              >
                {loadingSummary
                  ? "Loading..."
                  : "View Summary →"}
              </button>

            </div>

            {/* Flashcards */}

            <div className="dashboard-card">

              <div className="card-icon">
                ▣
              </div>

              <h2>
                Flashcards
              </h2>

              <p>
                Practice the material using
                AI-generated flashcards.
              </p>

              <button
                onClick={handlePractice}
              >
                {loadingFlashcards
                  ? "Loading..."
                  : "Practice →"}
              </button>

            </div>

            {/* Concepts */}

            <div className="dashboard-card">

              <div className="card-icon">
                ◎
              </div>

              <h2>
                Concepts
              </h2>

              <p>
                Explore the important concepts
                identified in your learning material.
              </p>

              <button
                onClick={handleExploreConcepts}
              >
                {loadingConcepts
                  ? "Loading..."
                  : "Explore Concepts →"}
              </button>

            </div>

            {/* AI Tutor */}

            <div className="dashboard-card">

              <div className="card-icon">
                ✧
              </div>

              <h2>
                AI Tutor
              </h2>

              <p>
                Ask questions and get answers
                grounded in your document.
              </p>

              <button
                onClick={() =>
                  document
                    .getElementById("ai-tutor")
                    ?.scrollIntoView({
                      behavior: "smooth",
                    })
                }
              >
                Start Learning →
              </button>

            </div>

          </div>

          {/* ==================================================
              SUMMARY
              ================================================== */}

          {summary && (
            <div className="summary-panel">

              <div className="summary-panel-header">

                <div>

                  <p className="eyebrow">
                    AI GENERATED
                  </p>

                  <h2>
                    Document Summary
                  </h2>

                </div>

                <button
                  onClick={() =>
                    setSummary(null)
                  }
                >
                  Close
                </button>

              </div>

              <div className="summary-content">

                <p>
                  {summary}
                </p>

              </div>

            </div>
          )}

          {/* ==================================================
              FLASHCARDS
              ================================================== */}

          {flashcards.length > 0 && (
            <div className="flashcard-panel">

              <div className="flashcard-header">

                <div>

                  <p className="eyebrow">
                    PRACTICE
                  </p>

                  <h2>
                    Flashcards
                  </h2>

                </div>

                <button
                  onClick={() => {
                    setFlashcards([]);
                    setShowAnswer(false);
                    setCurrentCard(0);
                  }}
                >
                  Close
                </button>

              </div>

              <div className="flashcard-progress">
                Card {currentCard + 1} of{" "}
                {flashcards.length}
              </div>

              <div className="flashcard">

                <p className="flashcard-label">
                  QUESTION
                </p>

                <h3>
                  {
                    flashcards[
                      currentCard
                    ].question
                  }
                </h3>

                {showAnswer && (
                  <div className="flashcard-answer">

                    <p className="flashcard-label">
                      ANSWER
                    </p>

                    <p>
                      {
                        flashcards[
                          currentCard
                        ].answer
                      }
                    </p>

                  </div>
                )}

              </div>

              <div className="flashcard-actions">

                <button
                  className="primary-action"
                  onClick={() =>
                    setShowAnswer(
                      !showAnswer
                    )
                  }
                >
                  {showAnswer
                    ? "Hide Answer"
                    : "Show Answer"}
                </button>

                <div className="navigation-buttons">

                  <button
                    disabled={
                      currentCard === 0
                    }
                    onClick={() => {
                      setCurrentCard(
                        currentCard - 1
                      );
                      setShowAnswer(false);
                    }}
                  >
                    ← Previous
                  </button>

                  <button
                    disabled={
                      currentCard ===
                      flashcards.length - 1
                    }
                    onClick={() => {
                      setCurrentCard(
                        currentCard + 1
                      );
                      setShowAnswer(false);
                    }}
                  >
                    Next →
                  </button>

                </div>

              </div>

            </div>
          )}

          {/* ==================================================
              CONCEPT GRAPH
              ================================================== */}

          {conceptGraph && (
            <div className="concept-panel">

              <div className="concept-panel-header">

                <div>

                  <p className="eyebrow">
                    CONCEPT MAP
                  </p>

                  <h2>
                    Explore Concepts
                  </h2>

                  <p>
                    Explore the important concepts
                    identified in your learning material.
                  </p>

                </div>

                <button
                  onClick={() =>
                    setConceptGraph(null)
                  }
                >
                  Close
                </button>

              </div>

              <div className="concept-map">

                {conceptGraph.nodes?.map(
                  (node, index) => (

                    <div
                      className="concept-node-wrapper"
                      key={node.id}
                    >

                      <div className="concept-node">

                        <div className="concept-node-number">
                          {String(index + 1).padStart(2, "0")}
                        </div>

                        <h3>
                          {node.label}
                        </h3>

                        <p>
                          {node.description}
                        </p>

                      </div>

                      {index <
                        conceptGraph.nodes.length - 1 && (
                        <div className="concept-connector">

                          <div className="connector-line"></div>

                          <div className="connector-arrow">
                            ↓
                          </div>

                        </div>
                      )}

                    </div>

                  )
                )}

              </div>

            </div>
          )}

          {/* ==================================================
              AI TUTOR
              ================================================== */}

          <div
            className="ai-tutor-panel"
            id="ai-tutor"
          >

            <div className="ai-tutor-header">

              <div>

                <p className="eyebrow">
                  AI TUTOR
                </p>

                <h2>
                  Ask your document
                </h2>

                <p>
                  Ask questions and get answers
                  grounded in your uploaded material.
                </p>

              </div>

              {messages.length > 0 && (
                <button
                  className="clear-chat-button"
                  onClick={() =>
                    setMessages([])
                  }
                >
                  Clear Chat
                </button>
              )}

            </div>

            {/* Chat */}

            <div className="chat-messages">

              {messages.length === 0 && (
                <div className="chat-empty">

                  <div className="chat-empty-icon">
                    ✧
                  </div>

                  <h3>
                    What would you like to learn?
                  </h3>

                  <p>
                    Ask a question about your
                    document and the AI tutor
                    will answer using the
                    learning material.
                  </p>

                </div>
              )}

              {messages.map(
                (message, index) => (
                  <div
                    key={index}
                    className={`chat-message ${
                      message.role === "user"
                        ? "user-message"
                        : "assistant-message"
                    }`}
                  >

                    <div className="message-role">
                      {message.role === "user"
                        ? "YOU"
                        : "AI TUTOR"}
                    </div>

                    <div className="message-content">
                      {message.content}
                    </div>

                    {message.role ===
                      "assistant" &&
                      message.sources?.length >
                        0 && (

                        <div className="message-sources">

                          <p className="sources-title">
                            SOURCES
                          </p>

                          {message.sources.map(
                            (
                              source,
                              sourceIndex
                            ) => (
                              <div
                                className="source-item"
                                key={sourceIndex}
                              >

                                <span>
                                  Source{" "}
                                  {sourceIndex + 1}
                                </span>

                                <p>
                                  {
                                    source.content
                                  }
                                </p>

                              </div>
                            )
                          )}

                        </div>
                      )}

                  </div>
                )
              )}

              {loadingTutor && (
                <div className="chat-message assistant-message">

                  <div className="message-role">
                    AI TUTOR
                  </div>

                  <div className="typing-indicator">

                    <span></span>
                    <span></span>
                    <span></span>

                  </div>

                </div>
              )}

            </div>

            {/* Suggested Questions */}

            {messages.length === 0 && (
              <div className="suggested-questions">

                <button
                  onClick={() =>
                    setQuestion(
                      "What is overfitting?"
                    )
                  }
                >
                  What is overfitting?
                </button>

                <button
                  onClick={() =>
                    setQuestion(
                      "How can overfitting be reduced?"
                    )
                  }
                >
                  How can overfitting be reduced?
                </button>

                <button
                  onClick={() =>
                    setQuestion(
                      "What is the main idea of this document?"
                    )
                  }
                >
                  Main idea?
                </button>

              </div>
            )}

            {/* Input */}

            <div className="chat-input-area">

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                onKeyDown={
                  handleTutorKeyDown
                }
                placeholder="Ask something about your document..."
                rows={2}
                disabled={loadingTutor}
              />

              <button
                className="send-button"
                onClick={handleAskTutor}
                disabled={
                  loadingTutor ||
                  !question.trim()
                }
              >
                {loadingTutor
                  ? "..."
                  : "Send →"}
              </button>

            </div>

            <p className="chat-hint">
              Press Enter to send · Shift +
              Enter for a new line
            </p>

          </div>

          {/* ==================================================
              DOCUMENT INFO
              ================================================== */}

          <div className="document-info">

            <span>
              Document ID
            </span>

            <strong>
              #{documentId}
            </strong>

          </div>

        </main>

      </div>
    );
  }

  // ============================================================
  // LANDING PAGE
  // ============================================================

  return (
    <div className="app">

      <header className="navbar">

        <div className="logo">
          Learning<span>AI</span>
        </div>

        <div className="nav-status">
          AI Learning Assistant
        </div>

      </header>

      <main className="main-content">

        <section className="hero">

          <div className="hero-content">

            <p className="eyebrow">
              AI-POWERED LEARNING
            </p>

            <h1>
              Turn your documents
              <br />
              into a{" "}
              <span>
                learning experience.
              </span>
            </h1>

            <p className="hero-description">
              Upload your study material and let
              AI create summaries, flashcards,
              concepts, and an interactive tutor
              grounded in your documents.
            </p>

            {/* Upload */}

            <div className="upload-card">

              <div className="upload-icon">
                ↑
              </div>

              <h2>
                Upload your document
              </h2>

              <p>
                PDF, DOCX, or TXT
              </p>

              <label className="upload-button">

                Choose File

                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  disabled={uploading}
                />

              </label>

              {file && (
                <>

                  <div className="selected-file">

                    <strong>
                      {file.name}
                    </strong>

                    <span>
                      {uploading
                        ? "Processing document..."
                        : "Ready to upload"}
                    </span>

                  </div>

                  <button
                    className="process-button"
                    onClick={handleUpload}
                    disabled={uploading}
                  >
                    {uploading
                      ? "Processing..."
                      : "Process Document →"}
                  </button>

                </>
              )}

            </div>

          </div>

          {/* Visual */}

          <div className="hero-visual">

            <div className="visual-card">

              <div className="visual-header">

                <span>
                  Learning AI
                </span>

                <span className="online-dot">
                  ●
                </span>

              </div>

              <div className="visual-content">

                <div className="visual-icon">
                  ✦
                </div>

                <h3>
                  Your personal AI tutor
                </h3>

                <p>
                  Ask questions, explore concepts,
                  and learn directly from your
                  study material.
                </p>

                <div className="feature-pill">
                  ✨ Grounded in your documents
                </div>

              </div>

            </div>

          </div>

        </section>

        {/* Features */}

        <section className="features">

          <div className="feature">

            <div className="feature-number">
              01
            </div>

            <h3>
              Understand
            </h3>

            <p>
              AI generates concise summaries
              and identifies the key concepts
              in your material.
            </p>

          </div>

          <div className="feature">

            <div className="feature-number">
              02
            </div>

            <h3>
              Practice
            </h3>

            <p>
              Automatically generated flashcards
              help you reinforce what you've learned.
            </p>

          </div>

          <div className="feature">

            <div className="feature-number">
              03
            </div>

            <h3>
              Ask
            </h3>

            <p>
              Chat with your material using a
              document-grounded AI tutor with
              source references.
            </p>

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;