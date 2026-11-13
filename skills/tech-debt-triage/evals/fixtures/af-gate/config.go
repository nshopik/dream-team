package watchdog

// Config is one anycast instance's probe settings.
type Config struct {
	Server    string // resolver under test, host:port
	ServesV4  bool
	ServesV6  bool
	TargetV4  string // name whose A record the probe asks for
	TargetV6  string // name whose AAAA record the probe asks for
	UnicastV4 string // address the A answer must contain
	UnicastV6 string // address the AAAA answer must contain
}
