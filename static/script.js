/**
 * Frontend logic for the LinkedIn Post Generator Agent.
 * Handles form submission, stage-tracker animation, API calls, and output rendering.
 */

const form = document.getElementById("post-form");
const generateBtn = document.getElementById("generate-btn");
const btnLabel = generateBtn.querySelector(".btn-label");
const btnSpinner = generateBtn.querySelector(".btn-spinner");
const formError = document.getElementById("form-error");
const outputError = document.getElementById("output-error");

const previewEmpty = document.getElementById("preview-empty");
const previewContent = document.getElementById("preview-content");
const previewActions = document.getElementById("preview-actions");

const outputHook = document.getElementById("output-hook");
const outputPost = document.getElementById("output-post");
const outputHashtags = document.getElementById("output-hashtags");

const copyBtn = document.getElementById("copy-btn");
const clearBtn = document.getElementById("clear-btn");

const stageTracker = document.getElementById("stage-tracker");
const stageItems = Array.from(stageTracker.querySelectorAll("li"));

let stageInterval = null;

/**
 * Animate the stage tracker to give visual feedback while the backend
 * pipeline (which takes several seconds due to multiple LLM calls) runs.
 * This is a client-side approximation, not a real progress stream.
 */
function startStageAnimation() {
  let index = 0;
  stageItems.forEach((li) => li.classList.remove("active", "done"));
  stageInterval = setInterval(() => {
    stageItems.forEach((li, i) => {
      li.classList.toggle("active", i === index);
      li.classList.toggle("done", i < index);
    });
    index = (index + 1) % stageItems.length;
  }, 1400);
}

function stopStageAnimation(markAllDone) {
  if (stageInterval) {
    clearInterval(stageInterval);
    stageInterval = null;
  }
  stageItems.forEach((li) => {
    li.classList.remove("active");
    li.classList.toggle("done", Boolean(markAllDone));
  });
}

function setLoading(isLoading) {
  generateBtn.disabled = isLoading;
  btnSpinner.hidden = !isLoading;
  btnLabel.textContent = isLoading ? "Drafting..." : "Draft the post";
  if (isLoading) {
    startStageAnimation();
  } else {
    stopStageAnimation(true);
  }
}

function hideErrors() {
  formError.hidden = true;
  formError.textContent = "";
  outputError.hidden = true;
  outputError.textContent = "";
}

function showFormError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

function showOutputError(message) {
  outputError.textContent = message;
  outputError.hidden = false;
}

function renderResult(data) {
  outputHook.textContent = data.hook;
  outputPost.textContent = data.post;
  outputHashtags.textContent = (data.hashtags || []).join("  ");

  previewEmpty.hidden = true;
  previewContent.hidden = false;
  previewActions.hidden = false;
}

function resetPreview() {
  previewEmpty.hidden = false;
  previewContent.hidden = true;
  previewActions.hidden = true;
  outputHook.textContent = "";
  outputPost.textContent = "";
  outputHashtags.textContent = "";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideErrors();

  const payload = {
    topic: document.getElementById("topic").value.trim(),
    audience: document.getElementById("audience").value.trim(),
    tone: document.getElementById("tone").value,
    length: document.getElementById("length").value,
    goal: document.getElementById("goal").value,
    keywords: document.getElementById("keywords").value.trim(),
  };

  if (!payload.topic || !payload.audience) {
    showFormError("Please fill in both the topic and target audience.");
    return;
  }

  setLoading(true);

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      const message = data.detail || data.error || "Something went wrong. Please try again.";
      showOutputError(typeof message === "string" ? message : JSON.stringify(message));
      resetPreview();
      return;
    }

    renderResult(data);
  } catch (err) {
    showOutputError("Could not reach the server. Please check your connection and try again.");
    resetPreview();
  } finally {
    setLoading(false);
  }
});

copyBtn.addEventListener("click", async () => {
  const fullText = `${outputHook.textContent}\n\n${outputPost.textContent}\n\n${outputHashtags.textContent}`;
  try {
    await navigator.clipboard.writeText(fullText);
    const original = copyBtn.textContent;
    copyBtn.textContent = "Copied!";
    setTimeout(() => { copyBtn.textContent = original; }, 1800);
  } catch (err) {
    showOutputError("Could not copy to clipboard. Please select and copy the text manually.");
  }
});

clearBtn.addEventListener("click", () => {
  form.reset();
  resetPreview();
  hideErrors();
  stopStageAnimation(false);
});
