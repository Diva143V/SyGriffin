# @griffin/griffin

Griffin is a model-agnostic, open-source AI research agent for scientific and ML engineering work. It runs a workspace in your browser where the agent plans tasks, writes and runs code, drives experiments, queries scientific databases, and writes up results. Bring your own API key or sign in with Atlas, use any frontier or open-weight model, and work with the bundled science skills.

Part of the [Griffin]() repository.

## Install

```bash
npm install -g @griffin/griffin
```

The command is `griffin`.

## Quick start

```bash
griffin                     # open the workspace in your browser
griffin ~/code/project      # open it in a specific directory
griffin connect login       # sign in to Atlas (optional; BYOK works without an account)
griffin run "..."           # run a one-shot task
```

Configuration lives in `~/.config/griffin/griffin.json`. Provider keys can be set in the workspace (bring your own key) or synced from Atlas.

## Docs

See the [repository README](#readme) for the full layout, provider setup, agent and skill architecture, and contribution guide.

## License

Apache License 2.0. See [LICENSE](/blob/main/LICENSE). Not affiliated with Anthropic.
