class StateMachine:
    def __init__(self, states, initial_state):
        """
        Initialize the state machine.
        :param states: A dictionary where keys are state names and values are lists of allowed next states.
        :param initial_state: The state where the state machine starts.
        """
        if initial_state not in states:
            raise ValueError(f"Invalid initial state: {initial_state}")

        self.states = states
        self.current_state = initial_state
        print(f"StateMachine initialized in '{self.current_state}' state.")

    def transition(self, next_state=None):
        """
        Transition from the current state to the next state if the transition is valid.
        :param next_state: The desired state to transition to.
        """
        if next_state is None:
            next_state = self.states[self.current_state][0]
            print(f"Transitioning to next state: {next_state}")
            self.current_state = next_state
        elif next_state in self.states[self.current_state]:
            print(f"Transitioning from '{self.current_state}' to '{next_state}'")
            self.current_state = next_state

    def get_state(self):
        """ Return the current state. """
        return self.current_state


# Example usage
if __name__ == "__main__":
    # Define states and allowed transitions
    states = {
        "IDLE": ["PROCESSING"],
        "PROCESSING": ["COMPLETED"],
        "COMPLETED": ["IDLE"],
    }

    sm = StateMachine(states, initial_state="IDLE")
    print("Current state:", sm.get_state())
    sm.transition()
    print("Current state:", sm.get_state())
    sm.transition()
    print("Current state:", sm.get_state())
    sm.transition()
    print("Current state:", sm.get_state())
    sm.transition()
    print("Current state:", sm.get_state())
