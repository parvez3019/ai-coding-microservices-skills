---
title: Microservices Skills — AI coding skills for Claude Code, Cursor and Codex
description: "21 composable AI skills that make Claude Code, Cursor and Codex write microservices with timeouts, circuit breakers, idempotency keys, authorisation and the right tests — not just code that works."
hide:
  - navigation
---

# Microservices Skills

**Composable AI skills that hold your coding assistant to microservices engineering standards —
boundary-aware, failure-aware, contract-first.** Works with Claude Code, Cursor, Codex and any
[Agent Skills](https://agentskills.io) host.

Ask an AI assistant to "add a call to the pricing service" and you get a working call. You usually
do not get a timeout, a circuit breaker, an idempotency key, an authorisation check scoped to the
caller, or a test for the path where pricing times out. Nothing is wrong with the code — it is just
missing everything that separates a demo from a service someone gets paged about.

## Before and after

The same prompt — *"call the pricing service when an order is placed"* — without and with the
skills installed. Illustrative, in the style of the [worked example](sample/index.md)'s Java stack.

=== "Without the skills"

    ```java
    public Order place(PlaceOrder cmd) {
        Price price = pricingClient.quote(cmd.sku(), cmd.quantity());
        return orders.save(Order.from(cmd, price));
    }
    ```

=== "With the skills"

    ```java
    public Order place(PlaceOrder cmd, Caller caller) {
        authz.requireCanOrderFor(caller, cmd.customerId());          // secure-service
        return idempotency.once(cmd.idempotencyKey(), () -> {         // idempotency-and-immutability
            Price price = pricing.quote(cmd.sku(), cmd.quantity());   // adapter: 800 ms timeout,
                                                                      // retry budget, breaker,
                                                                      // fails closed — resilience-patterns
            return orders.save(Order.place(cmd, price));              // invariant lives on Order — domain-modelling
        });
    }
    // + component test for "pricing times out → 503, no order written" — test-strategy
    ```

Every comment on the right is a check one of the skills ran before the code was shown to you.

## Install in one line

```bash
claude plugin marketplace add parvez3019/ai-coding-microservices-skills && \
claude plugin install microservices-skills@ai-coding-microservices-skills --yes
```

Cursor, Codex and other hosts: see [Getting Started](getting-started.md).

## What you get

<div class="grid cards" markdown>

-   :material-shield-check-outline: **16 principles**

    ---

    Guardrails that load automatically: [service boundaries](skills/service-boundaries/index.md),
    [resilience](skills/resilience-patterns/index.md), [API contracts](skills/api-contracts/index.md),
    [security](skills/secure-service/index.md), [testing](skills/test-strategy/index.md) and more.

-   :material-source-branch: **4 workflows**

    ---

    [`/design-service`](skills/design-service/index.md) →
    [`/implement-service`](skills/implement-service/index.md) →
    [`/review-service`](skills/review-service/index.md), plus
    [`/refactor-safely`](skills/refactor-safely/index.md).

-   :material-card-account-details-outline: **1 profile**

    ---

    [`/stack-profile`](skills/stack-profile/index.md) records your language, framework and broker,
    so every check speaks your team's actual libraries.

-   :material-account-search-outline: **Independent reviewer**

    ---

    A [subagent](agents/microservice-reviewer.md) that audits code with no memory of having
    written it.

</div>

[Browse all skills](skills/index.md){ .md-button .md-button--primary }
[See the worked example](sample/index.md){ .md-button }

## Design principles

- **Checks over advice.** "Services should be resilient" changes nothing. *"Does this call have an
  explicit timeout shorter than the caller's deadline? If not, set one derived from the latency
  budget"* changes the output.
- **Composability over one big document.** Small single-purpose skills load only when relevant;
  workflows compose them.
- **Judgment handed back, not hidden.** Sync or async, strong or eventual consistency, split or keep
  together — every skill lists the calls it must not make silently and routes them back to you with
  options and a recommendation.
