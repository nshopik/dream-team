---
allowed_tools: [Read, Grep, Glob, Skill]
---

Use the brainstorm skill, then answer.

Session so far:
[user] I have an idea: the resolver should stop answering ANY queries in full, we keep seeing them in amplification attacks. Not sure how far to go.
[assistant] The answer path is `src/answer.rs`; nothing special-cases ANY today, and no spec covers it. Round 1: 1. Answer ANY with the minimal response from RFC 8482, or refuse it? Recommended: the RFC 8482 minimal answer. 2. Every client, or UDP only? Recommended: UDP only; a TCP client cannot spoof its address. 3. Configurable? Recommended: one on/off config key, default on.
[user] 1 RFC 8482. 2 UDP only. 3 one key, default on.
[assistant] Round 2: 1. Count minimized answers? Recommended: one counter, `any_minimized_total`, in the existing `src/metrics.rs` registry.
[user] Yes, add the counter. That's everything I had.
[assistant] - **Idea:** answer ANY queries over UDP with the RFC 8482 minimal response
- **Settled:** response — RFC 8482 minimal answer
- **Settled:** scope — UDP only
- **Settled:** config — one on/off key, default on
- **Settled:** metrics — `any_minimized_total` counter in `src/metrics.rs`
- **Path:** issue — adds a config key and a counter the user decided on
[user] Yes, file the issue.

You are the assistant in this session. Take your next step on the user's last message. You cannot run commands: show the message you would send the user.
