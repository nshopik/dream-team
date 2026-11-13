package watchdog

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// Registered in init() of server.go.
var (
	probesTotal = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "watchdog_probes_total",
		Help: "Probes run, by address family and result.",
	}, []string{"af", "result"})
	withdrawalsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "watchdog_withdrawals_total",
		Help: "Times an address family's prefix was withdrawn.",
	}, []string{"af"})
)
