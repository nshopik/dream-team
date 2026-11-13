package watchdog

import (
	"fmt"
	"testing"
)

func TestProber_writesOnFlip(t *testing.T) {
	var writes []string
	p := NewProber(func(af string, up bool) error {
		writes = append(writes, fmt.Sprintf("%s=%t", af, up))
		return nil
	})
	for _, r := range []struct {
		af string
		ok bool
	}{{"v6", true}, {"v6", false}, {"v6", false}, {"v4", true}, {"v6", true}} {
		p.Record(r.af, r.ok)
	}
	if got, want := fmt.Sprint(writes), "[v6=false v6=true]"; got != want {
		t.Fatalf("writes = %s, want %s", got, want)
	}
}
