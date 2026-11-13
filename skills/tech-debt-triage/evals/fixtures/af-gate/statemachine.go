package watchdog

// StateMachine debounces probe results into an announce or withdraw decision.
type StateMachine struct {
	withdrawAfter, riseAfter int
	fails, oks               int
	up                       bool
}

func NewStateMachine(withdrawAfter, riseAfter int) *StateMachine {
	return &StateMachine{withdrawAfter: withdrawAfter, riseAfter: riseAfter, up: true}
}

func (s *StateMachine) Observe(ok bool) {
	if ok {
		s.fails, s.oks = 0, s.oks+1
	} else {
		s.oks, s.fails = 0, s.fails+1
	}
	if s.up && s.fails >= s.withdrawAfter {
		s.up = false
	} else if !s.up && s.oks >= s.riseAfter {
		s.up = true
	}
}

func (s *StateMachine) Up() bool { return s.up }
