import os, sys
import threading
import msvcrt
import secrets
from src.rules import RULES
from src.patterns import set_pattern

def handle_input(self):
    try:
        if os.name == 'nt':
            while True:
                if msvcrt.kbhit() and not handle_key(self, msvcrt.getch().decode('utf-8').lower()): break
        else:
            import termios, tty
            fd, old = sys.stdin.fileno(), termios.tcgetattr(sys.stdin.fileno())
            tty.setraw(fd)
            while True:
                if not handle_key(self, sys.stdin.read(1).lower()): break
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except (OSError, termios.error) as e:
        print(f"Error handling terminal input: {e}")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def handle_key(self, key):
    if key == ' ': self.running = not self.running or threading.Thread(target=self.simulate, daemon=True).start()
    elif key == 'r': set_pattern(self, 'single')
    elif key == 'n': self.rule_num = list(RULES.keys())[(list(RULES.keys()).index(self.rule_num)+1) % len(RULES)]
    elif key == 'p': set_pattern(self, secrets.choice(['single', 'double', 'triple', 'random', 'edges', 'symmetric']))
    elif key == 'q': return False
    return True
