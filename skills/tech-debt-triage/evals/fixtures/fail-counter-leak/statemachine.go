package watchdog

// StateMachine debounces probe results into an announce or withdraw decision.
type StateMachine struct {
	withdrawAfter int // consecutive failures before Up turns false
	riseAfter     int // consecutive successes before Up turns true
	failCount     int
	okCount       int
	up            bool
}

// up starts true so a restart does not withdraw a healthy prefix; Prober.seed handles the rest.
func NewStateMachine(cfg Config) *StateMachine {
	return &StateMachine{withdrawAfter: cfg.WithdrawAfter, riseAfter: cfg.RiseAfter, up: true}
}

// Observe feeds one probe result and reports whether Up changed.
func (s *StateMachine) Observe(ok bool) bool {
	if ok {
		s.failCount, s.okCount = 0, s.okCount+1
	} else {
		s.okCount, s.failCount = 0, s.failCount+1
	}
	was := s.up
	switch {
	case s.up && s.failCount >= s.withdrawAfter:
		s.up = false
	case !s.up && s.okCount >= s.riseAfter:
		s.up = true
	}
	return s.up != was
}

func (s *StateMachine) Up() bool { return s.up }

func (s *StateMachine) fails() int { return s.failCount }
