package main

import "time"

type Prober struct {
	interval time.Duration
}

func (p *Prober) probe() {}

// Run probes once per interval and beats sup after each probe. Register "prober" with sup
// before calling Run: a loop that stalls before its first beat is never tracked.
func (p *Prober) Run(sup *Supervisor) {
	for range time.Tick(p.interval) {
		p.probe()
		sup.Beat("prober")
	}
}
