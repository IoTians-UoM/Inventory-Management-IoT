import time


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

    def transition(self, next_state):
        """
        Transition from the current state to the next state if the transition is valid.
        :param next_state: The desired state to transition to.
        """
        if next_state in self.states[self.current_state]:
            print(f"Transitioning from '{self.current_state}' to '{next_state}'.")
            self.current_state = next_state
        else:
            raise ValueError(f"Invalid transition from '{self.current_state}' to '{next_state}'.")

    def get_state(self):
        """ Return the current state. """
        return self.current_state

    def run(self):
        """
        Example run loop. Override this method for custom behavior.
        """
        print("Starting state machine loop. Press Ctrl+C to exit.")
        try:
            while True:
                print(f"Current State: {self.current_state}")
                time.sleep(2)

                # Example transitions (override or modify as needed)
                if self.current_state == "IDLE":
                    self.transition("PROCESSING")
                elif self.current_state == "PROCESSING":
                    self.transition("COMPLETED")
                elif self.current_state == "COMPLETED":
                    print("Process completed. Resetting to IDLE.")
                    self.transition("IDLE")

        except KeyboardInterrupt:
            print("Stopping state machine.")


# ✅ Example usage
if __name__ == "__main__":
    # Define states and allowed transitions
    states = {
        "IDLE": ["PROCESSING"],
        "PROCESSING": ["COMPLETED", "ERROR"],
        "COMPLETED": ["IDLE"],
        "ERROR": ["IDLE"]
    }

    sm = StateMachine(states, initial_state="IDLE")
    sm.run()
