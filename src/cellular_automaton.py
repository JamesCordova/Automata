import os, time, threading, sys
from src.rules import RULES
from src.patterns import set_pattern
from src.input_handler import handle_input

WIDTH, SPEED, ALIVE, DEAD = 60, 0.2, '■', '·'

class CellularAutomaton:
    def __init__(self):
        self.state, self.generation, self.running, self.rule_num = [0] * WIDTH, 0, False, 30
        self.history, self.max_history = [], 25
        
    def get_rule_table(self): 
        return RULES.get(self.rule_num, RULES[30])
    
    def apply_rule(self, left, center, right): 
        pattern = (left << 2) + (center << 1) + right
        return self.get_rule_table()[pattern]
    
    def next_generation(self):
        self.state = [(self.apply_rule(self.state[(i-1) % WIDTH], self.state[i], self.state[(i+1) % WIDTH])) for i in range(WIDTH)]
        self.history.append(self.state[:])
        if len(self.history) > self.max_history: 
            self.history.pop(0)
        self.generation += 1
    
    def display(self):
        screen = f"\033[2J\033[H┌{'─' * WIDTH}┐\n"
        for i, hist_state in enumerate(self.history[-15:]):
            alpha = '90' if i < 10 else '37'
            row = "│" + ''.join(f'\033[{alpha}m{ALIVE}\033[0m' if cell else DEAD for cell in hist_state) + "│\n"
            screen += row
        screen += "│" + ''.join(f'\033[93m{ALIVE}\033[0m' if cell else DEAD for cell in self.state) + "│\n"
        screen += f"└{'─' * WIDTH}┘\nGen: {self.generation:4d} | Rule: {self.rule_num:3d} | Speed: {1/SPEED:.1f}x | Cells: {sum(self.state):3d}\n"
        screen += "[SPACE] Play/Pause | [R] Reset | [N] Next Rule | [P] Pattern | [Q] Quit"
        print(screen, end='', flush=True)
    
    def get_input(self):
        handle_input(self)
    
    def simulate(self):
        while self.running: 
            self.next_generation()
            time.sleep(SPEED)
    
    def run(self):
        if os.name != 'nt': os.system('stty -echo')
        set_pattern(self, 'single')
        threading.Thread(target=self.get_input, daemon=True).start()
        try:
            while True: 
                self.display() 
                time.sleep(0.1)
        except KeyboardInterrupt:
            if os.name != 'nt': 
                os.system('stty echo')
            print("\n\nSimulación terminada.")
