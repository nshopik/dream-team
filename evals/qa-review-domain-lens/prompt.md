---
allowed_tools: [Read, Grep, Glob, Skill]
---

/dream-team:qa-review

Session so far:
[assistant] The repo is the RADIUS proxy. The session model is opus. The forge is unreachable. Read CLAUDE.md, in full:
```
# CLAUDE.md

- Detail the code doesn't show goes in the commit message or a topic doc under docs/, never in package docs.
- A fact the code and paths don't show has one doc under docs/, updated in the MR that changes it.
- Name a new milestone M<n>; a split takes the next free M<n>, never a letter.
- Every Access-Reject the proxy sends carries a Reply-Message attribute.
- Never write a User-Password or Message-Authenticator value to a log.
- Run `go test ./...` before every commit.
```
README.md reads "radproxy: a RADIUS proxy that forwards Access-Requests to an upstream server pool." docs/ holds `rfc2865.txt`, the vendored text of RFC 2865, and `proxy-timeouts.md`. `git merge-base HEAD origin/main` is `4f1c2ab`. `git diff --stat 4f1c2ab`:
```
 proxy/upstream.go      | 14 +++++++++-----
 proxy/upstream_test.go | 22 ++++++++++++++++++++++
 2 files changed, 31 insertions(+), 5 deletions(-)
```
`git diff 4f1c2ab -- proxy/upstream.go`:
```
@@ -40,11 +40,14 @@ func (p *Pool) Forward(req *radius.Packet) (*radius.Packet, error) {
-	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
+	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
 	defer cancel()
-	return p.next().Exchange(ctx, req)
+	resp, err := p.next().Exchange(ctx, req)
+	if err != nil {
+		return p.next().Exchange(ctx, req)
+	}
+	return resp, nil
 }
```


You are the assistant in this session. Take your next step. You cannot run commands or launch agents: list every Agent call you would make, with its full prompt, then stop.
