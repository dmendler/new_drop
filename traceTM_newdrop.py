#!/usr/bin/env python3

import csv
import sys
from collections import defaultdict, deque

class NonDeterministicTM:
    def __init__(self, file_path):
        self.rules = defaultdict(list)  # Maps (current_state, read_symbol) -> [(next_state, write_symbol, direction)]
        self.all_states = set()
        self.input_symbols = set()
        self.tape_symbols = set()
        self.start = None
        self.accept = None
        self.reject = None
        self.depth_limit = 100
        self.transition_limit = 1000
        self.load_from_file(file_path)
    
    def load_from_file(self, file_path):
        """Load TM definition from a CSV file."""
        with open(file_path, mode="r") as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)
        
        self.name = rows[0][0]
        self.all_states = set(rows[1])
        self.input_symbols = set(rows[2])
        self.tape_symbols = set(rows[3])
        self.start = rows[4][0]
        self.accept = rows[5][0]
        self.reject = rows[6][0]
        
        for rule in rows[7:]:
            current_state, read_symbol, next_state, write_symbol, move_dir = rule
            self.rules[(current_state, read_symbol)].append((next_state, write_symbol, move_dir))

    def execute(self, input_data, max_depth=100, max_steps=1000):
        """Simulate the TM using a breadth-first approach."""
        self.depth_limit = max_depth
        self.transition_limit = max_steps

        initial_state = ["", self.start, input_data]  # [tape_left, current_state, tape_right]
        config_tree = [[initial_state]]  # Tree of configurations
        steps_count = 0

        print(f"Machine Name: {self.name}")
        print(f"Initial String: '{input_data}'")

        while config_tree and steps_count < self.transition_limit:
            current_level = config_tree[-1]
            next_level = []

            for tape_left, current_state, tape_right in current_level:
                if current_state == self.accept:
                    # Trace and halt on acceptance
                    print(f"String accepted in {steps_count} transitions.")
                    print(f"Tree reach depth of {len(config_tree) - 1}")
                    self.print_accept_path(config_tree, len(config_tree) - 1)
                    return

                if current_state == self.reject:
                    continue  # Skip rejected paths

                # Read the symbol under the head
                current_symbol = tape_right[0] if tape_right else "_"
                steps_count += 1

                if steps_count > self.transition_limit:
                    print(f"Execution stopped after {self.transition_limit} transitions.")
                    return

                # Fetch possible transitions
                transitions = self.rules.get((current_state, current_symbol), [])

                if not transitions:
                    # No valid transitions, move to reject state
                    next_level.append([tape_left, self.reject, tape_right])
                    continue

                # Apply each transition
                for next_state, write_symbol, move_dir in transitions:
                    new_left, new_right = list(tape_left), list(tape_right)

                    # Write the symbol
                    if new_right:
                        new_right[0] = write_symbol
                    else:
                        new_right.append(write_symbol)

                    # Move the head
                    if move_dir == "L":
                        if new_left:
                            new_right.insert(0, new_left.pop())
                        else:
                            new_right.insert(0, "_")
                    elif move_dir == "R":
                        if new_right:
                            new_left.append(new_right.pop(0))
                        if not new_right:
                            new_right.append("_")

                    # Append the new configuration
                    next_level.append(["".join(new_left), next_state, "".join(new_right)])

            # Add next level configurations
            if next_level:
                config_tree.append(next_level)

            # Check depth limit
            if len(config_tree) > self.depth_limit:
                print(f"Execution stopped after reaching max depth of {self.depth_limit}.")
                print(f"Tree Depth: {self.depth_limit}, Total Transitions: {steps_count}")
                return

            # Check if all paths reject
            if not any(cfg[1] != self.reject for cfg in next_level):
                print(f"String rejected after {len(config_tree) - 1} steps.")
                print(f"Tree Depth: {len(config_tree) - 1}, Total Transitions: {steps_count}")
                return

        print("No valid paths found. TM halted.")

    def print_accept_path(self, tree, depth):
        """Trace and print the path to the accept state."""
        num_configs = 0
        for level in range(depth + 1):
            for config in tree[level]:
                num_configs += 1
                print(f"Level {level}: {config}")
        print(f"Number configurations explored: {num_configs}")
        print(f"Average non-determinisim: {num_configs/depth}")

def main():
    machine_file = input("Enter the Turing Machine definition file: ")
    input_data = input("Enter the input string: ")
    max_depth = int(input("Enter max depth (default 100): ") or 100)
    max_steps = int(input("Enter max transitions (default 1000): ") or 1000)

    turing_machine = NonDeterministicTM(machine_file)
    turing_machine.execute(input_data, max_depth, max_steps)

if __name__ == "__main__":
    main()
