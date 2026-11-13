package watchdog

type Config struct {
	WithdrawAfter int
	RiseAfter     int
}

// Prober turns probe results into ready.conf writes.
type Prober struct {
	cfg    Config
	sm     *StateMachine
	write  func(up bool) error // writes ready.conf and reconfigures bird
	seeded bool                // ready.conf written since start
	force  bool                // write on this step even if Up did not change
}

func NewProber(cfg Config, write func(bool) error) *Prober {
	return &Prober{cfg: cfg, sm: NewStateMachine(cfg), write: write}
}

// Step feeds one probe result and writes ready.conf when bird must change.
func (p *Prober) Step(ok bool) error {
	changed := p.sm.Observe(ok)
	if !p.seeded {
		// After a restart ready.conf may still hold the last run's value: write the first
		// decision, either the first success or as many failures as a withdraw takes.
		if ok || p.sm.fails() >= p.cfg.WithdrawAfter {
			p.seeded, p.force = true, true
		}
	}
	if !changed && !p.force {
		return nil
	}
	p.force = false
	return p.write(p.sm.Up())
}
