package main

import (
	"flag"
	"time"
)

func main() {
	interval := flag.Duration("interval", time.Second, "probe interval")
	flag.Parse()
	p := &Prober{interval: *interval}
	// The prober beats once per interval; allow three missed beats.
	sup := NewSupervisor(3 * *interval)
	// Register before starting the prober, or a stall before its first beat goes unseen.
	sup.Register("prober")
	go p.Run(sup)
	sup.Run(*interval)
}
