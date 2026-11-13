package watchdog

// Prober withdraws or re-announces an address family's prefix when its probe result flips.
type Prober struct {
	up    map[string]bool
	write func(af string, up bool) error // writes ready.conf and reconfigures bird
}

func NewProber(write func(string, bool) error) *Prober {
	return &Prober{up: map[string]bool{"v4": true, "v6": true}, write: write}
}

// Record counts one probe result and writes ready.conf when af's state flips.
func (p *Prober) Record(af string, ok bool) error {
	result := "ok"
	if !ok {
		result = "fail"
	}
	probesTotal.WithLabelValues(af, result).Inc()
	if p.up[af] == ok {
		return nil
	}
	if err := p.write(af, ok); err != nil {
		return err
	}
	p.up[af] = ok
	if !ok {
		withdrawalsTotal.WithLabelValues(af).Inc()
	}
	return nil
}
