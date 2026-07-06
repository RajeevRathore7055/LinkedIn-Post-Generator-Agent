"""
Core AI Agent workflow for the LinkedIn Post Generator.

This module implements a true multi-stage agent pipeline rather than a single
prompt call. Each stage has a single responsibility and feeds its output into
the next stage, mimicking a plan -> act -> refine agentic loop.

Workflow:
    understand_request()
        -> create_post_plan()
        -> generate_hook()
        -> generate_post()
        -> improve_post()
        -> generate_hashtags()
        -> return_final_post()
"""

import logging

from app.models import PostRequest, PostResponse
from app.prompts import (
    hashtag_generation_prompt,
    hook_generation_prompt,
    intent_analysis_prompt,
    planning_prompt,
    post_generation_prompt,
    readability_improvement_prompt,
)
from app.utils import call_llm, parse_hashtags

logger = logging.getLogger("linkedin_agent")


def understand_request(request: PostRequest) -> str:
    """
    Stage 1: Analyze the user's request to extract underlying intent.

    Args:
        request: Validated user input.

    Returns:
        A short natural-language summary of the user's intent.
    """
    logger.info("Stage 1: Understanding request intent.")
    prompt = intent_analysis_prompt(request)
    return call_llm(prompt)


def create_post_plan(request: PostRequest, intent_summary: str) -> str:
    """
    Stage 2: Create a structural outline/plan for the post.

    Args:
        request: Validated user input.
        intent_summary: Output from understand_request().

    Returns:
        A bullet-point plan/outline as text.
    """
    logger.info("Stage 2: Creating post plan.")
    prompt = planning_prompt(request, intent_summary)
    return call_llm(prompt)


def generate_hook(request: PostRequest, plan: str) -> str:
    """
    Stage 3: Generate an engaging hook (opening line).

    Args:
        request: Validated user input.
        plan: Output from create_post_plan().

    Returns:
        A single hook line.
    """
    logger.info("Stage 3: Generating hook.")
    prompt = hook_generation_prompt(request, plan)
    hook = call_llm(prompt)
    return hook.strip().strip('"')


def generate_post(request: PostRequest, plan: str, hook: str) -> str:
    """
    Stage 4: Generate the main LinkedIn post body.

    Args:
        request: Validated user input.
        plan: Output from create_post_plan().
        hook: Output from generate_hook().

    Returns:
        A draft LinkedIn post as text.
    """
    logger.info("Stage 4: Generating main post content.")
    prompt = post_generation_prompt(request, plan, hook)
    return call_llm(prompt)


def improve_post(draft_post: str, request: PostRequest) -> str:
    """
    Stage 5: Improve readability, formatting, and emoji usage of the draft.

    Args:
        draft_post: Output from generate_post().
        request: Validated user input.

    Returns:
        A polished, readability-improved post.
    """
    logger.info("Stage 5: Improving readability.")
    prompt = readability_improvement_prompt(draft_post, request)
    return call_llm(prompt)


def generate_hashtags(request: PostRequest, final_post: str) -> list[str]:
    """
    Stage 6: Generate relevant hashtags for the final post.

    Args:
        request: Validated user input.
        final_post: Output from improve_post().

    Returns:
        A list of hashtag strings.
    """
    logger.info("Stage 6: Generating hashtags.")
    prompt = hashtag_generation_prompt(request, final_post)
    raw = call_llm(prompt)
    return parse_hashtags(raw)


def return_final_post(hook: str, post: str, hashtags: list[str]) -> PostResponse:
    """
    Stage 7: Assemble the final structured response.

    Args:
        hook: The generated hook line.
        post: The final polished post body.
        hashtags: List of generated hashtags.

    Returns:
        A PostResponse object ready to be serialized to the client.
    """
    logger.info("Stage 7: Returning final assembled post.")
    return PostResponse(hook=hook, post=post, hashtags=hashtags)


def run_agent_pipeline(request: PostRequest) -> PostResponse:
    """
    Orchestrate the full agent pipeline end-to-end.

    Args:
        request: Validated user input from the /generate endpoint.

    Returns:
        The final PostResponse containing hook, post, and hashtags.
    """
    intent_summary = understand_request(request)
    plan = create_post_plan(request, intent_summary)
    hook = generate_hook(request, plan)
    draft_post = generate_post(request, plan, hook)
    final_post = improve_post(draft_post, request)
    hashtags = generate_hashtags(request, final_post)
    return return_final_post(hook, final_post, hashtags)
