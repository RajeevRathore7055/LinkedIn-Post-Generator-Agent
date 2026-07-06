"""
Reusable, structured prompt templates for each stage of the agent workflow.

Keeping prompts isolated here makes them easy to tune independently without
touching the agent orchestration logic in agent.py.
"""

from app.models import PostRequest


def intent_analysis_prompt(request: PostRequest) -> str:
    """Prompt to help the model understand the user's underlying intent."""
    return f"""You are analyzing a request to write a LinkedIn post.

Topic: {request.topic}
Target Audience: {request.audience}
Tone: {request.tone.value}
Goal: {request.goal.value}
Keywords: {request.keywords or "None provided"}

In 2-3 short sentences, summarize:
1. What the author really wants to communicate.
2. What emotional or professional impression they want to leave on the audience.

Respond only with plain text, no headings, no markdown."""


def planning_prompt(request: PostRequest, intent_summary: str) -> str:
    """Prompt to create a structural plan for the post before writing it."""
    return f"""You are planning the structure of a LinkedIn post.

Intent summary: {intent_summary}

Topic: {request.topic}
Audience: {request.audience}
Tone: {request.tone.value}
Length: {request.length.value}
Goal: {request.goal.value}
Keywords to weave in naturally: {request.keywords or "None"}

Create a short bullet-point outline (3-5 bullets) covering:
- The opening angle
- The core message / story / value point(s)
- The closing call-to-action or takeaway

Respond only with the outline as plain text bullets, no extra commentary."""


def hook_generation_prompt(request: PostRequest, plan: str) -> str:
    """Prompt to generate a scroll-stopping first line (hook)."""
    return f"""You are an expert LinkedIn copywriter.

Write ONE powerful hook line (max 15 words) for a LinkedIn post based on this plan:

{plan}

Tone: {request.tone.value}
Goal: {request.goal.value}

Rules:
- No hashtags.
- No emojis unless tone is Friendly or Inspirational.
- Must create curiosity or emotional pull.
- Return ONLY the hook line, nothing else."""


def post_generation_prompt(request: PostRequest, plan: str, hook: str) -> str:
    """Prompt to write the main body of the LinkedIn post."""
    length_guidance = {
        "Short": "80-120 words",
        "Medium": "150-220 words",
        "Long": "250-350 words",
    }
    target_length = length_guidance.get(request.length.value, "150-220 words")

    return f"""You are an expert LinkedIn ghostwriter.

Write a complete LinkedIn post using this hook as the opening line:
"{hook}"

Outline to follow:
{plan}

Requirements:
- Target length: {target_length}
- Tone: {request.tone.value}
- Audience: {request.audience}
- Goal: {request.goal.value}
- Naturally include these keywords if relevant: {request.keywords or "None"}
- Use short paragraphs (1-3 lines each) with line breaks for LinkedIn readability.
- Include the hook as the first line.
- End with a clear takeaway or call-to-action aligned with the goal.
- Do NOT include hashtags in this output (they will be added separately).
- Do NOT include emojis unless the tone calls for it (Friendly, Inspirational, Marketing).

Return ONLY the post text."""


def readability_improvement_prompt(draft_post: str, request: PostRequest) -> str:
    """Prompt to refine and polish the draft post for readability."""
    return f"""You are a professional editor specializing in LinkedIn content.

Improve the following LinkedIn post draft for:
- Readability (short lines, good spacing, scannability)
- Clarity and flow
- Appropriate emoji usage (only if it fits a {request.tone.value} tone, used sparingly)
- Keeping the original meaning and structure intact

Draft:
{draft_post}

Return ONLY the improved final post text, formatted for LinkedIn with line breaks."""


def hashtag_generation_prompt(request: PostRequest, final_post: str) -> str:
    """Prompt to generate relevant, high-quality hashtags."""
    return f"""Based on this LinkedIn post, generate 5 to 8 relevant, high-quality hashtags.

Post:
{final_post}

Topic: {request.topic}
Goal: {request.goal.value}
Keywords: {request.keywords or "None"}

Rules:
- Mix of broad and niche hashtags.
- No spaces within a hashtag.
- No duplicate or overly generic hashtags like #post or #linkedin.
- Return ONLY a comma-separated list of hashtags, each starting with #."""
