const askForm = document.getElementById("ask-form");
const outputEl = document.getElementById("output");
const expertsEl = document.getElementById("experts");
const overallFeedbackEl = document.getElementById("overall-feedback");
const rawJsonDetailsEl = document.getElementById("raw-json");
const rawJsonContentEl = document.getElementById("raw-json-content");
const errorEl = document.getElementById("error");
const logoutBtn = document.getElementById("logout");

let currentQuestionId = null;

function safeJsonParse(value) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function simpleHash(str) {
  // Small non-crypto hash for stable localStorage keys.
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(16);
}

function feedbackStorageKey({ questionId, question, expertName, linkedinUrl }) {
  const raw = JSON.stringify({
    qid: questionId || "",
    q: question || "",
    n: expertName || "",
    l: linkedinUrl || "",
  });
  return `expert_finder.feedback.${simpleHash(raw)}`;
}

function overallFeedbackStorageKey(question) {
  return `expert_finder.overall_feedback.${simpleHash(question || "")}`;
}

function loadFeedback(key) {
  try {
    return safeJsonParse(localStorage.getItem(key)) || { score: null, note: "" };
  } catch {
    return { score: null, note: "" };
  }
}

function saveFeedback(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore storage errors (private mode, quota, etc.)
  }
}

function loadOverallFeedback(key) {
  try {
    return safeJsonParse(localStorage.getItem(key)) || { note: "" };
  } catch {
    return { note: "" };
  }
}

function saveOverallFeedback(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore storage errors (private mode, quota, etc.)
  }
}

function extractLinkedInUrl(expert) {
  const profile = expert && expert.profile;
  if (!profile || typeof profile !== "object") return null;

  if (typeof profile.linkedin_url === "string" && profile.linkedin_url) {
    return profile.linkedin_url;
  }

  const sources = [];
  if (Array.isArray(profile.education)) sources.push(...profile.education);
  if (Array.isArray(profile.professional)) sources.push(...profile.professional);

  for (const item of sources) {
    const url = item && item.linkedin_url;
    if (typeof url === "string" && url) return url;
  }

  return null;
}

function computeExpertKey({ questionId, questionText, expertName, linkedinUrl, index }) {
  const raw = JSON.stringify({
    qid: questionId || "",
    q: questionText || "",
    n: expertName || "",
    l: linkedinUrl || "",
    i: index,
  });
  return simpleHash(raw);
}

function renderOverallFeedback(questionForStorage) {
  if (!overallFeedbackEl) return;
  overallFeedbackEl.textContent = "";
  if (!questionForStorage) return;

  const storageKey = overallFeedbackStorageKey(questionForStorage);
  const saved = loadOverallFeedback(storageKey);
  let savedNote = saved && typeof saved.note === "string" ? saved.note : "";
  let draftNote = savedNote;

  const card = document.createElement("div");
  card.className = "overall-feedback-card";

  const title = document.createElement("p");
  title.className = "overall-feedback-title";
  title.textContent = "Feedback on these results";

  const help = document.createElement("p");
  help.className = "overall-feedback-help";
  help.textContent =
    "Use this only for question-level feedback (coverage, location, missing roles/seniority, or search breadth).";

  const disclaimer = document.createElement("p");
  disclaimer.className = "overall-feedback-disclaimer";
  disclaimer.textContent =
    "For feedback about a specific suggestion, use the score/note controls on that expert’s card.";

  const textarea = document.createElement("textarea");
  textarea.className = "overall-feedback-textarea";
  textarea.rows = 2;
  textarea.placeholder = "Optional feedback about the overall answer…";
  textarea.value = savedNote;

  const footer = document.createElement("div");
  footer.className = "expert-footer";

  const footerLeft = document.createElement("div");
  footerLeft.className = "expert-footer-left";

  const footerRight = document.createElement("div");
  footerRight.className = "expert-footer-right";

  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "expert-note-toggle";
  toggle.textContent = savedNote ? "Edit feedback" : "Add feedback";

  let open = false;
  textarea.hidden = true;

  toggle.addEventListener("click", () => {
    open = !open;
    textarea.hidden = !open;
    toggle.textContent = open ? "Hide feedback" : savedNote ? "Edit feedback" : "Add feedback";
    if (open) textarea.focus();
  });

  const savedEl = document.createElement("span");
  savedEl.className = "expert-feedback-saved";
  savedEl.textContent = "Saved";
  savedEl.hidden = true;

  let savedTimer = null;
  function flashSaved() {
    savedEl.hidden = false;
    if (savedTimer) window.clearTimeout(savedTimer);
    savedTimer = window.setTimeout(() => {
      savedEl.hidden = true;
      savedTimer = null;
    }, 900);
  }

  const sendBtn = document.createElement("button");
  sendBtn.type = "button";
  sendBtn.className = "expert-send";
  sendBtn.textContent = "Send feedback";
  sendBtn.disabled = true;

  function isDirty() {
    return draftNote !== savedNote;
  }

  function updateDirty() {
    sendBtn.disabled = !isDirty();
  }

  textarea.addEventListener("input", () => {
    draftNote = textarea.value || "";
    updateDirty();
  });

  sendBtn.addEventListener("click", () => {
    saveOverallFeedback(storageKey, { note: draftNote });
    savedNote = draftNote;
    updateDirty();
    toggle.textContent = open ? "Hide feedback" : savedNote ? "Edit feedback" : "Add feedback";
    flashSaved();
  });

  footerLeft.appendChild(toggle);
  footerRight.appendChild(savedEl);
  footerRight.appendChild(sendBtn);
  footer.appendChild(footerLeft);
  footer.appendChild(footerRight);

  card.appendChild(title);
  card.appendChild(help);
  card.appendChild(disclaimer);
  card.appendChild(footer);
  card.appendChild(textarea);
  overallFeedbackEl.appendChild(card);
}

function renderExperts(experts, { questionId, questionText }) {
  if (!expertsEl) return;
  expertsEl.textContent = "";

  if (!Array.isArray(experts) || experts.length === 0) {
    return;
  }

  const fragment = document.createDocumentFragment();
  experts.forEach((expert, idx) => {
    const card = document.createElement("article");
    card.className = "expert-card";

    const header = document.createElement("div");
    header.className = "expert-header";

    const number = document.createElement("div");
    number.className = "expert-number";
    number.textContent = `#${idx + 1}`;

    const name = document.createElement("div");
    name.className = "expert-name";
    name.textContent = (expert && expert.name) || "Unknown";

    header.appendChild(number);
    header.appendChild(name);

    const linkedinUrl = extractLinkedInUrl(expert);
    const expertName = (expert && expert.name) || "Unknown";
    const expertKey = computeExpertKey({
      questionId,
      questionText,
      expertName,
      linkedinUrl: linkedinUrl || "",
      index: idx + 1,
    });
    const storageKey = feedbackStorageKey({
      questionId: questionId || "",
      question: questionText || "",
      expertName: expertName || "",
      linkedinUrl: linkedinUrl || "",
    });
    const savedFeedback = loadFeedback(storageKey);
    let savedScore =
      savedFeedback && (savedFeedback.score === 1 || savedFeedback.score === 2 || savedFeedback.score === 3)
        ? savedFeedback.score
        : null;
    let savedNote = savedFeedback && typeof savedFeedback.note === "string" ? savedFeedback.note : "";

    let draftScore = savedScore;
    let draftNote = savedNote;

    const actions = document.createElement("div");
    actions.className = "expert-actions";

    if (linkedinUrl) {
      const link = document.createElement("a");
      link.className = "expert-linkedin";
      link.href = linkedinUrl;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "LinkedIn Profile";
      actions.appendChild(link);
    }

    const scoreGroup = document.createElement("div");
    scoreGroup.className = "expert-score expert-score--header";
    scoreGroup.setAttribute("role", "radiogroup");
    scoreGroup.setAttribute("aria-label", "Score (1 to 3)");

    const noteToggle = document.createElement("button");
    noteToggle.type = "button";
    noteToggle.className = "expert-note-toggle";
    noteToggle.textContent = "Add note";

    const note = document.createElement("div");
    note.className = "expert-note";
    note.hidden = true;

    const textarea = document.createElement("textarea");
    textarea.className = "expert-note-textarea";
    textarea.rows = 2;
    textarea.placeholder = "Why this match is good/bad? (optional)";
    textarea.addEventListener("input", () => {
      draftNote = textarea.value || "";
      updateDirty();
    });

    note.appendChild(textarea);

    noteToggle.addEventListener("click", () => {
      note.hidden = !note.hidden;
      noteToggle.textContent = note.hidden ? "Add note" : "Hide note";
      if (!note.hidden) textarea.focus();
    });

    const footer = document.createElement("div");
    footer.className = "expert-footer";

    const footerLeft = document.createElement("div");
    footerLeft.className = "expert-footer-left";

    const footerRight = document.createElement("div");
    footerRight.className = "expert-footer-right";

    const sendBtn = document.createElement("button");
    sendBtn.type = "button";
    sendBtn.className = "expert-send";
    sendBtn.textContent = "Send feedback";
    sendBtn.disabled = true;

    const saved = document.createElement("span");
    saved.className = "expert-feedback-saved";
    saved.textContent = "Saved";
    saved.hidden = true;

    const feedbackError = document.createElement("span");
    feedbackError.className = "expert-feedback-error";
    feedbackError.hidden = true;

    let savedTimer = null;
    function flashSaved() {
      saved.hidden = false;
      if (savedTimer) window.clearTimeout(savedTimer);
      savedTimer = window.setTimeout(() => {
        saved.hidden = true;
        savedTimer = null;
      }, 900);
    }

    function isValidScore(v) {
      return v === 1 || v === 2 || v === 3;
    }

    function isDirty() {
      return draftScore !== savedScore || draftNote !== savedNote;
    }

    function updateDirty() {
      sendBtn.disabled = !(isDirty() && isValidScore(draftScore));
    }

    function setScore(nextScore) {
      draftScore = nextScore;
      btns.forEach((b, idx2) => {
        const s = idx2 + 1;
        const isSelected = s === draftScore;
        b.classList.toggle("selected", isSelected);
        b.setAttribute("aria-checked", isSelected ? "true" : "false");
      });
      updateDirty();
    }

    sendBtn.addEventListener("click", async () => {
      if (!isValidScore(draftScore)) return;
      if (!questionId) {
        feedbackError.textContent = "Missing question id. Please re-run the question.";
        feedbackError.hidden = false;
        return;
      }

      feedbackError.hidden = true;
      const prevText = sendBtn.textContent;
      sendBtn.textContent = "Sending...";
      sendBtn.disabled = true;

      try {
        const response = await fetch("/api/feedback/expert", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question_id: questionId,
            expert_key: expertKey,
            expert_name: expertName,
            expert_linkedin_url: linkedinUrl || null,
            score: draftScore,
            note: draftNote ? draftNote : null,
          }),
        });

        if (response.status === 401) {
          window.location.href = "/login";
          return;
        }

        if (!response.ok) {
          const payload = await response.json().catch(() => null);
          feedbackError.textContent =
            (payload && payload.detail) || "Could not send feedback. Please try again.";
          feedbackError.hidden = false;
          return;
        }

        // Keep a local copy as well (useful for UX / offline-ish behavior).
        saveFeedback(storageKey, { score: draftScore, note: draftNote });
        savedScore = draftScore;
        savedNote = draftNote;
        updateDirty();
        flashSaved();
      } catch (e) {
        feedbackError.textContent = "Network error. Please try again.";
        feedbackError.hidden = false;
      } finally {
        sendBtn.textContent = prevText;
        updateDirty();
      }
    });

    const btns = [1, 2, 3].map((score) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "expert-score-pill";
      b.textContent = String(score);
      b.setAttribute("role", "radio");
      b.setAttribute("aria-checked", "false");
      b.setAttribute("aria-label", `Score ${score} of 3`);
      b.addEventListener("click", () => {
        setScore(score);
      });
      scoreGroup.appendChild(b);
      return b;
    });

    if (savedScore === 1 || savedScore === 2 || savedScore === 3) {
      setScore(savedScore);
    } else {
      updateDirty();
    }
    if (savedNote) {
      textarea.value = savedNote;
      note.hidden = false;
      noteToggle.textContent = "Hide note";
    }

    actions.appendChild(scoreGroup);
    header.appendChild(actions);

    const reason = document.createElement("div");
    reason.className = "expert-reason";
    reason.textContent = (expert && expert.reason) || "";

    card.appendChild(header);
    card.appendChild(reason);

    footerLeft.appendChild(noteToggle);
    footerRight.appendChild(feedbackError);
    footerRight.appendChild(saved);
    footerRight.appendChild(sendBtn);
    footer.appendChild(footerLeft);
    footer.appendChild(footerRight);

    card.appendChild(footer);
    card.appendChild(note);

    fragment.appendChild(card);
  });

  expertsEl.appendChild(fragment);
}

function renderRawJson(payload) {
  if (!rawJsonDetailsEl || !rawJsonContentEl) return;
  rawJsonDetailsEl.open = false;
  rawJsonContentEl.textContent = payload ? JSON.stringify(payload, null, 2) : "";
}

if (askForm && outputEl && errorEl) {
  askForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorEl.textContent = "";
    if (expertsEl) expertsEl.textContent = "";
    if (overallFeedbackEl) overallFeedbackEl.textContent = "";
    renderRawJson(null);
    const questionInput = document.getElementById("question");
    const question = questionInput ? questionInput.value.trim() : "";
    if (!question) {
      errorEl.textContent = "Question is required.";
      return;
    }

    outputEl.textContent = "Running...";
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (response.status === 401) {
      window.location.href = "/login";
      return;
    }

    const payload = await response.json();
    if (!response.ok) {
      errorEl.textContent = payload.detail || "Request failed.";
      outputEl.textContent = "";
      return;
    }

    renderRawJson(payload);
    renderOverallFeedback(payload && payload.question ? payload.question : question);
    const experts = payload && payload.result && payload.result.experts;
    if (!Array.isArray(experts) || experts.length === 0) {
      outputEl.textContent = "No experts found for this question.";
      return;
    }

    outputEl.textContent = "Suggested experts:";
    currentQuestionId = payload && payload.question_id ? payload.question_id : null;
    renderExperts(experts, {
      questionId: currentQuestionId,
      questionText: payload && payload.question ? payload.question : question,
    });
  });
}

if (logoutBtn) {
  logoutBtn.addEventListener("click", async () => {
    await fetch("/logout", { method: "POST" });
    window.location.href = "/login";
  });
}

