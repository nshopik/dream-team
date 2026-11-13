package main

import (
	"log"
	"sync"
	"time"
)

// Supervisor exits the process when a registered loop stops beating, so systemd restarts it.
type Supervisor struct {
	mu         sync.Mutex
	last       map[string]time.Time
	staleAfter time.Duration
}

func NewSupervisor(staleAfter time.Duration) *Supervisor {
	return &Supervisor{last: map[string]time.Time{}, staleAfter: staleAfter}
}

func (s *Supervisor) Register(name string) { s.Beat(name) }

func (s *Supervisor) Beat(name string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.last[name] = time.Now()
}

// Run is started by main after the metrics HTTP server.
func (s *Supervisor) Run(tick time.Duration) {
	for range time.Tick(tick) {
		s.mu.Lock()
		for name, t := range s.last {
			if age := time.Since(t); age > s.staleAfter {
				log.Fatalf("supervisor: %s stale for %s", name, age)
			}
		}
		s.mu.Unlock()
	}
}
