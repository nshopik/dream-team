package watchdog

import (
	"context"
	"log"
	"net"
)

// Probe asks server for target's address record and reports whether the answer holds expected.
func Probe(ctx context.Context, server, af, qtype, target, expected, proto string) bool {
	r := &net.Resolver{PreferGo: true, Dial: func(ctx context.Context, _, _ string) (net.Conn, error) {
		var d net.Dialer
		return d.DialContext(ctx, proto, server)
	}}
	network := "ip4"
	if qtype == "AAAA" {
		network = "ip6"
	}
	ips, err := r.LookupIP(ctx, network, target)
	if err != nil {
		log.Printf("probe %s %s %s: %v", af, qtype, target, err)
		return false
	}
	for _, ip := range ips {
		if ip.String() == expected {
			return true
		}
	}
	log.Printf("probe %s %s %s: %v lacks %s", af, qtype, target, ips, expected)
	return false
}
