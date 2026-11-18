---
title: Getting Started — install microservices skills in Claude Code, Cursor or Codex
description: "Install the Microservices Skills plugin in Claude Code, Cursor, Codex or any Agent Skills host, then profile your stack, design, implement and review a service."
---

# Getting Started

Every option installs the same skills from the same `skills/` folder; the host manifests are thin
pointers, not copies.

## 1. Install

=== "Claude Code"

    In the chat:

    ```
    /plugin marketplace add parvez3019/ai-coding-microservices-skills
    /plugin install microservices-skills@ai-coding-microservices-skills
    ```

    Or from the terminal, non-interactively:

    ```bash
    claude plugin marketplace add parvez3019/ai-coding-microservices-skills
    claude plugin install microservices-skills@ai-coding-microservices-skills --yes
    ```

    Type `/` in a session — the skills appear as `/microservices-skills:design-service`, and as
    bare `/design-service` when the name is unambiguous. Includes the
    [`microservice-reviewer`](agents/microservice-reviewer.md) subagent.

=== "Cursor"

    Add the repository from **Cursor Settings → Customize → Plugins**:

    ```
    https://github.com/parvez3019/ai-coding-microservices-skills
    ```

    Or vendor the skills into a project, so the standards are versioned and reviewed with the
    code:

    ```bash
    git clone https://github.com/parvez3019/ai-coding-microservices-skills.git
    cd ai-coding-microservices-skills
    ./tools/install.sh /path/to/your-service/.cursor/skills
    ```

    Cursor has no subagents, so `/review-service` runs as a single pass.

=== "Codex"

    ```bash
    codex plugin marketplace add parvez3019/ai-coding-microservices-skills
    codex plugin add microservices-skills@ai-coding-microservices-skills
    codex plugin list | grep -i microservices
    ```

=== "Any other host"

    The skills are plain [Agent Skills](https://agentskills.io) markdown:

    ```bash
    git clone https://github.com/parvez3019/ai-coding-microservices-skills.git
    cd ai-coding-microservices-skills
    ./tools/install.sh ~/.claude/skills                    # Claude Code, all projects
    ./tools/install.sh /absolute/path/to/that/tool/skills  # anything else
    ```

## 2. Profile the project

Run [`/stack-profile`](skills/stack-profile/index.md) in the AI chat. It reads the repository,
asks only about what it could not detect, and writes `.msskills/stack.md` plus a starter
`.msskills/config.yaml`.

## 3. Design

Run [`/design-service <feature>`](skills/design-service/index.md). It climbs the four design
levels, stopping for approval at each, and leaves an approved blueprint in `.msskills/designs/`.

## 4. Implement

Run [`/implement-service`](skills/implement-service/index.md). It builds from that blueprint
inside-out, layer by layer, running every applicable checklist before presenting anything.

## 5. Review

Run [`/review-service`](skills/review-service/index.md). It audits the change against every
principle and reports severity-ranked findings anchored to files and lines.

The principles need no invocation. Writing an HTTP client pulls in
[`infrastructure-adapters`](skills/infrastructure-adapters/index.md),
[`resilience-patterns`](skills/resilience-patterns/index.md) and
[`secure-service`](skills/secure-service/index.md); writing a migration pulls in
[`data-access`](skills/data-access/index.md).

!!! tip "See it before you run it"
    The [worked example](sample/index.md) shows a filled-in stack profile and an approved blueprint
    for a realistic `orders-service`.
