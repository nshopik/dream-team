# CLAUDE.md

- Build with `go build ./...`; test with `go test ./...`; lint with `golangci-lint run`.
- Keep `internal/encode/` under the perf gate: run `BenchmarkEncodeBatch` on the lab host before
  merging a change there.
- Run issues labelled `docs` through dream-fixer's light tier.
