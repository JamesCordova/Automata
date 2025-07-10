WIDTH = 60

def set_pattern(self, pattern_name):
    patterns = {
        'single': [(WIDTH//2, 1)], 
        'double': [(WIDTH//2-1, 1), (WIDTH//2+1, 1)],
        'triple': [(WIDTH//2-1, 1), (WIDTH//2, 1), (WIDTH//2+1, 1)],
        'random': [(i, 1) for i in range(0, WIDTH, 3) if i % 7 == 0], 
        'edges': [(5, 1), (WIDTH-6, 1)], 
        'symmetric': [(WIDTH//2-10, 1), (WIDTH//2-5, 1), (WIDTH//2, 1), (WIDTH//2+5, 1), (WIDTH//2+10, 1)]
    }
    self.state = [0] * WIDTH
    for pos, val in patterns.get(pattern_name, []): 
        if 0 <= pos < WIDTH: self.state[pos] = val
    self.generation, self.history = 0, [self.state[:]]
