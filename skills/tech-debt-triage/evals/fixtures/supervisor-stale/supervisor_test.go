package main

import (
	"errors"
	"os"
	"os/exec"
	"testing"
	"time"
)

// Run exits through log.Fatalf, so the stale case runs in a child copy of this test binary.
func TestSupervisor_staleLoopExits(t *testing.T) {
	if os.Getenv("SUPERVISOR_CHILD") == "1" {
		s := NewSupervisor(50 * time.Millisecond)
		s.Register("prober")
		s.Run(10 * time.Millisecond)
		return
	}
	cmd := exec.Command(os.Args[0], "-test.run=^TestSupervisor_staleLoopExits$")
	cmd.Env = append(os.Environ(), "SUPERVISOR_CHILD=1")
	var exit *exec.ExitError
	if err := cmd.Run(); !errors.As(err, &exit) || exit.ExitCode() != 1 {
		t.Fatalf("child: %v, want exit status 1", err)
	}
}
