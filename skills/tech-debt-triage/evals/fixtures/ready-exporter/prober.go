package watchdog

import (
	"fmt"
	"os"
	"os/exec"

	"github.com/prometheus/client_golang/prometheus"
)

var announced = prometheus.NewGaugeVec(prometheus.GaugeOpts{
	Name: "watchdog_announced",
	Help: "1 while bird announces the anycast prefix for the address family.",
}, []string{"af"})

// InstanceProber keeps bird's ready.conf in step with one instance's probe results.
type InstanceProber struct {
	confPath string
	up       map[string]bool // by address family: "v4", "v6"
	applied  string
}

func NewInstanceProber(confPath string) *InstanceProber {
	return &InstanceProber{confPath: confPath, up: map[string]bool{"v4": true, "v6": true}}
}

// Set records a probe result; called from tick().
func (p *InstanceProber) Set(af string, up bool) error {
	p.up[af] = up
	return p.reconcile()
}

func (p *InstanceProber) reconcile() error {
	conf := fmt.Sprintf("define READY_V4 = %t;\ndefine READY_V6 = %t;\n", p.up["v4"], p.up["v6"])
	if conf == p.applied {
		return nil
	}
	if err := os.WriteFile(p.confPath, []byte(conf), 0o644); err != nil {
		return err
	}
	if out, err := exec.Command("birdc", "configure").CombinedOutput(); err != nil {
		// ready.conf is written and bird reads it on its next reload, so report it as announced.
		for af, up := range p.up {
			announced.WithLabelValues(af).Set(gauge(up))
		}
		return fmt.Errorf("birdc configure: %v: %s", err, out)
	}
	p.applied = conf
	p.setAnnounced()
	return nil
}

func (p *InstanceProber) setAnnounced() {
	announced.WithLabelValues("v4").Set(gauge(p.up["v4"]))
	announced.WithLabelValues("v6").Set(gauge(p.up["v4"]))
}

func gauge(b bool) float64 {
	if b {
		return 1
	}
	return 0
}
