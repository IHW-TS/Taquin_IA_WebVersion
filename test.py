import heapq
from collections import deque
import time
import os 
from random import shuffle


class Taquin:
    def __init__(self, state, parent=None, move=None, g=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.g = g

    def get_neighbors(self):
            neighbors = []
            moves = [('N', (-1, 0)), ('S', (1, 0)), ('E', (0, 1)), ('W', (0, -1))]
            x, y = None, None

            for i, row in enumerate(self.state):
                for j, cell in enumerate(row):
                    if cell == 0:
                        x, y = i, j
                        break
                if x is not None:
                    break

            for move, (dx, dy) in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(self.state) and 0 <= ny < len(self.state[0]):
                    new_state = [row.copy() for row in self.state]
                    new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                    neighbors.append(Taquin(new_state, parent=self, move=move, g=self.g + 1))

            return neighbors

    def get_distance(self, i, j):
        target_x, target_y = divmod(self.state[i][j] - 1, len(self.state[0]))
        return abs(target_x - i) + abs(target_y - j)


    def h(self, heuristic):
        if heuristic == 6:
            return sum(self.get_distance(i, j) for i in range(len(self.state)) for j in range(len(self.state[0])) if self.state[i][j] != 0)
        else:
            weights = [
                [36, 12, 12,  4,  1,  1,  4,  0],
                [ 8,  7,  6,  5,  4,  3,  2,  1],
                [ 8,  7,  6,  5,  3,  2,  4,  1],
            ]

            if heuristic == 1:
                pi = weights[0]
            elif heuristic in [2, 3]:
                pi = weights[1]
            elif heuristic in [4, 5]:
                pi = weights[2]

            pk = 4 if heuristic in [1, 3, 5] else 1

            return sum(pi[self.state[i][j] - 1] * self.get_distance(i, j) for i in range(len(self.state)) for j in range(len(self.state[0])) if self.state[i][j] != 0) // pk

    def f(self, heuristic):
        return self.g + self.h(heuristic)

    def __lt__(self, other):
        return self.state < other.state
    
def solve_taquin(initial_state, final_state, heuristic):
    initial_taquin = Taquin(initial_state)
    frontier = [(initial_taquin.f(heuristic), initial_taquin)]
    explored = set()
    num_explored = 0

    while frontier:
        _, current = heapq.heappop(frontier)

        if current.state == final_state:
            solution = deque()
            while current.parent is not None:
                solution.appendleft(current.move)
                current = current.parent
            return solution, num_explored

        explored.add(tuple(map(tuple, current.state)))
        num_explored += 1

        for neighbor in current.get_neighbors():
            if tuple(map(tuple, neighbor.state)) not in explored:
                heapq.heappush(frontier, (neighbor.f(heuristic), neighbor))

    return None, num_explored

def generate_random_state(size):
    state = list(range(size * size))
    shuffle(state)
    return [state[i * size:(i + 1) * size] for i in range(size)]

def generate_states(size):
    initial_state = generate_random_state(size)
    final_state = [[(i * size + j + 1) % (size * size) for j in range(size)] for i in range(size)]
    return initial_state, final_state

def print_taquin(state):
    for row in state:
        print(' '.join(str(cell) for cell in row))
    print()

if __name__ == "__main__":
    size = int(input("Veuillez entrer la taille du taquin (par exemple, 3 pour un taquin 3x3): "))
    initial_state, final_state = generate_states(size)

    print("État initial du taquin :")
    print_taquin(initial_state)

    heuristic = int(input("Veuillez choisir le poids à utiliser (1-6): "))

    start_time = time.time()
    solution, num_explored = solve_taquin(initial_state, final_state, heuristic)
    execution_time = time.time() - start_time

    if solution:
        print(f"Nombre d'états explorés: {num_explored}")
        print(f"Nombre de coups joués: {len(solution)}")
        print(f"Solution pour heuristique h{heuristic}: {solution}")
        print(f"Temps d'exécution: {execution_time:.2f} secondes")
        print(f"Temps CPU: {os.times()[0]:.2f} secondes")

        current_state = initial_state
        taquin_instance = Taquin(current_state)
        total_distance = taquin_instance.h(heuristic)
        print(f"Estimation de la distance restante: {total_distance - len(solution)}")
        print(f"Estimation de la fonction heuristique: {total_distance}")

        print("État final du taquin :")
        for move in solution:
            for neighbor in taquin_instance.get_neighbors():
                if neighbor.move == move:
                    taquin_instance = neighbor
                    break
        print_taquin(taquin_instance.state)
    else:
        print(f"Pas de solution trouvée pour heuristique h{heuristic}.")