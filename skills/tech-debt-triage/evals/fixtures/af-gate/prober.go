package watchdog

import (
	"context"
	"fmt"
	"strings"
)

type Prober struct {
	cfg        Config
	smV4, smV6 *StateMachine
}

func NewProber(cfg Config) *Prober {
	return &Prober{cfg: cfg, smV4: NewStateMachine(3, 2), smV6: NewStateMachine(3, 2)}
}

// tick probes each address family the instance serves and returns ready.conf.
func (p *Prober) tick(ctx context.Context) string {
	var b strings.Builder
	if p.cfg.ServesV4 {
		ok := Probe(ctx, p.cfg.Server, "v4", "A", p.cfg.TargetV4, p.cfg.UnicastV4, "udp")
		p.smV4.Observe(ok)
		fmt.Fprintf(&b, "define %s = %t;\n", readyVar("v4"), p.smV4.Up())
	}
	if p.cfg.ServesV6 {
		ok := Probe(ctx, p.cfg.Server, "v6", "AAAA", p.cfg.TargetV6, p.cfg.UnicastV6, "udp")
		p.smV6.Observe(ok)
		fmt.Fprintf(&b, "define %s = %t;\n", readyVar("v6"), p.smV6.Up())
	}
	return b.String()
}

// readyVar names the bird variable for af, e.g. ready_v4.
func readyVar(af string) string { return "READY_" + strings.ToUpper(af) }
