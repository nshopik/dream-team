package watchdog

import (
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/prometheus/client_golang/prometheus/testutil"
)

// stubBirdc puts a birdc on PATH that exits with code.
func stubBirdc(t *testing.T, code int) {
	t.Helper()
	dir := t.TempDir()
	script := fmt.Sprintf("#!/bin/sh\nexit %d\n", code)
	if err := os.WriteFile(filepath.Join(dir, "birdc"), []byte(script), 0o755); err != nil {
		t.Fatal(err)
	}
	t.Setenv("PATH", dir)
}

func TestInstanceProber_v6FailDrainsOnlyV6(t *testing.T) {
	stubBirdc(t, 1)
	p := NewInstanceProber(filepath.Join(t.TempDir(), "ready.conf"))
	p.Set("v6", false)
	if got := testutil.ToFloat64(announced.WithLabelValues("v4")); got != 1 {
		t.Errorf("v4 announced = %v, want 1", got)
	}
	if got := testutil.ToFloat64(announced.WithLabelValues("v6")); got != 0 {
		t.Errorf("v6 announced = %v, want 0", got)
	}
}
