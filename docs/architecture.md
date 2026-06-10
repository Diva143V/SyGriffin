# Griffin Architecture

Griffin is a CLI-first pipeline. Deterministic skills live in `griffin.bio` and `griffin.integrations`; agents in `griffin.agents` interpret and orchestrate scientific decisions; `griffin.pipeline` coordinates stage order, artifacts, checkpoints, and manifests.

The MVP runs offline in deterministic mock-safe mode by default. Live integrations can replace mock clients without changing the pipeline contract.

