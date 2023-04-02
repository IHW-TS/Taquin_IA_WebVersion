import heapq # Import du module heapq pour utiliser une file de priorité
from collections import deque # Import du module deque pour utiliser une liste doublement chaînée
import time # Import du module time pour mesurer le temps d'exécution
import os # Import du module os pour mesurer le temps CPU
from random import shuffle

class Taquin:
    # Initialisation d'un objet Taquin avec une configuration (état), un parent (état précédent),
    # un mouvement (dernier mouvement effectué) et le coût total pour atteindre cet état
    def __init__(self, state, parent=None, move=None, g=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.g = g

    # Récupération des voisins possibles de l'état actuel
    def get_neighbors(self):
        neighbors = [] # Initialisation de la liste des voisins
        moves = [('N', (-1, 0)), ('S', (1, 0)), ('E', (0, 1)), ('W', (0, -1))] # Les mouvements possibles

        # Initialisation des variables x et y à None
        x, y = None, None

        # Recherche de la case vide (0) dans l'état actuel du Taquin
        for i, row in enumerate(self.state):
            for j, cell in enumerate(row):
                if cell == 0:
                    x, y = i, j # Enregistre les coordonnées de la case vide
                    break
            if x is not None:
                break # Sort de la boucle lorsque la case vide est trouvée

        for move, (dx, dy) in moves:
            nx, ny = x + dx, y + dy # Nouvelle position
            if 0 <= nx < len(self.state) and 0 <= ny < len(self.state[0]): # Vérification de la validité de la position
                new_state = [row.copy() for row in self.state] # Copie de l'état actuel
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y] # Echange de la case vide avec la case voisine
                neighbors.append(Taquin(new_state, parent=self, move=move, g=self.g + 1)) # Ajout du voisin avec le coût mis à jour

        return neighbors

    # Calcul de la distance de Manhattan entre la case courante et la case cible
    def get_distance(self, i, j):
        target_x, target_y = divmod(self.state[i][j] - 1, len(self.state[0]))
        return abs(target_x - i) + abs(target_y - j)

    # Calcul de la distance heuristique en utilisant soit la somme des distances de Manhattan de toutes les cases,
    # soit une heuristique pondérée plus complexe
    def h(self, heuristic):
        if heuristic == 6: # Heuristique 6 : somme des distances de Manhattan de toutes les cases
            return sum(self.get_distance(i, j) for i in range(len(self.state)) for j in range(len(self.state[0])) if self.state[i][j] != 0)
        else: # Autres heuristiques : heuristique pondérée plus complexe
            weights = [ # Pondérations pour chaque case
                [36, 12, 12,  4,  1,  1,  4,  0],
                [ 8,  7,  6,  5,  4,  3,  2,  1],
                [ 8,  7,  6,  5,  3,  2,  4,  1],
            ]

            if heuristic == 1: # Heuristique 1 : somme des distances de Manhattan pour chaque case
                pi = weights[0]
            elif heuristic in [2, 3]: # Heuristiques 2 et 3 : pondération différente pour les cases du bord et du coin
                pi = weights[1]
            elif heuristic in [4, 5]: # Heuristiques 4 et 5 : pondération différente pour les cases du bord et du coin
                pi = weights[2]

            pk = 4 if heuristic in [1, 3, 5] else 1 # Facteur de normalisation pour les pondérations

            # Calcul de la valeur de l'heuristique pondérée
            return sum(pi[self.state[i][j] - 1] * self.get_distance(i, j) for i in range(len(self.state)) for j in range(len(self.state[0])) if self.state[i][j] != 0) // pk

    def f(self, heuristic):
        return self.g + self.h(heuristic) # Calcul de la valeur de la fonction d'évaluation f

    def __lt__(self, other):
        return self.state < other.state # Comparaison entre deux états du Taquin en se basant sur l'ordre lexicographique

    
def solve_taquin(initial_state, final_state, heuristic):
    initial_taquin = Taquin(initial_state) # Création de l'état initial
    frontier = [(initial_taquin.f(heuristic), initial_taquin)] # Initialisation de la file de priorité avec l'état initial
    explored = set()  # Initialisation de l'ensemble des états explorés
    num_explored = 0 # Initialisation du nombre d'états explorés

    while frontier: # Tant qu'il y a des états dans la file de priorité
        _, current = heapq.heappop(frontier) # Récupération de l'état avec le coût minimum

        if current.state == final_state: # Si l'état courant est l'état final
            solution = deque() # Initialisation de la liste des mouvements
            while current.parent is not None: # Tant qu'il y a des parents
                solution.appendleft(current.move) # Ajout du mouvement à la liste
                current = current.parent # Passage au parent suivant
            return solution, num_explored 

        explored.add(tuple(map(tuple, current.state))) # Ajout de l'état courant à l'ensemble des états explorés
        num_explored += 1 

        for neighbor in current.get_neighbors(): # Pour chaque voisin de l'état courant
            if tuple(map(tuple, neighbor.state)) not in explored: # Si le voisin n'a pas déjà été exploré
                heapq.heappush(frontier, (neighbor.f(heuristic), neighbor)) # Ajout du voisin à la file de priorité avec le coût mis à jour

    return None, num_explored

def generate_random_state(size):
    # Crée une liste contenant des entiers allant de 0 à size*size-1, inclus
    state = list(range(size * size))
    # Mélange les entiers de manière aléatoire
    shuffle(state)
    # Regroupe les entiers en sous-listes de taille size pour former une matrice carrée
    return [state[i * size:(i + 1) * size] for i in range(size)]

def is_valid_state(state):

    size = len(state) # Taille de l'état (nombre de rangées)
    flat_state = [cell for row in state for cell in row] # Convertit l'état 2D en une liste à plat

    expected_state = list(range(size * size)) # Crée l'état cible avec toutes les cases en ordre croissant
    expected_state[-1] = 0 # La dernière case doit être vide

    inversions = 0 # Compteur d'inversions (paires de cases mal placées)

    # Parcourt chaque case de l'état à plat
    for i, cell in enumerate(flat_state):
        # Compare la case avec toutes les cases suivantes
        for j in range(i + 1, size * size):
            # Vérifie si la case suivante est plus petite et non vide
            if flat_state[j] and flat_state[j] < cell:
                inversions += 1 # Incrémente le compteur d'inversions

    if size % 2 == 1: # Si la taille de l'état est impaire
        return inversions % 2 == 0 # Retourne vrai si le nombre d'inversions est pair, faux sinon
    else: # Si la taille de l'état est paire
        empty_row = next(i for i, row in enumerate(state) if 0 in row) # Trouve la rangée de la case vide
        return (inversions + empty_row) % 2 == 1 # Retourne vrai si le nombre d'inversions plus la rangée de la case vide est impair, faux sinon

# Fonction pour générer un état de Taquin valide de taille "size"
def generate_states(size):
    initial_state = generate_random_state(size) # Génère un état initial aléatoire
    while not is_valid_state(initial_state): # Tant que l'état n'est pas valide
        initial_state = generate_random_state(size) # Génère un nouvel état initial aléatoire
    final_state = [[(i * size + j + 1) % (size * size) for j in range(size)] for i in range(size)] # Génère l'état final
    return initial_state, final_state 

# Fonction pour afficher l'état actuel du Taquin
def print_taquin(state):
    for row in state:
        print(' '.join(str(cell) for cell in row))
    print()

if __name__ == "__main__":
    size = int(input("Veuillez entrer la taille du taquin (par exemple, 3 pour un taquin 3x3): "))
    
    # Génère un état initial et final de Taquin de la taille demandée
    initial_state, final_state = generate_states(size)

    # Affiche l'état initial du Taquin
    print("État initial du taquin :")
    print_taquin(initial_state)

    # Demande à l'utilisateur le poids à utiliser pour l'heuristique
    heuristic = int(input("Veuillez choisir le poids à utiliser (1-6): "))

    # Résout le Taquin en utilisant l'algorithme A* avec la fonction solve_taquin()
    start_time = time.time()
    solution, num_explored = solve_taquin(initial_state, final_state, heuristic)
    execution_time = time.time() - start_time

    if solution: # Si une solution a été trouvée
        # Affiche le nombre d'états explorés, le nombre de coups joués, la solution, le temps d'exécution et le temps CPU
        print(f"Nombre d'états explorés: {num_explored}")
        print(f"Nombre de coups joués: {len(solution)}")
        print(f"Solution pour heuristique h{heuristic}: {solution}")
        print(f"Temps d'exécution: {execution_time:.2f} secondes")
        print(f"Temps CPU: {os.times()[0]:.2f} secondes")

        # Calcule la distance restante et la fonction heuristique à partir de l'état final du Taquin
        current_state = initial_state
        taquin_instance = Taquin(current_state)
        total_distance = taquin_instance.h(heuristic)
        print(f"Estimation de la distance restante: {total_distance - len(solution)}")
        print(f"Estimation de la fonction heuristique: {total_distance}")

        # Affiche l'état final du Taquin en parcourant la solution trouvée
        print("État final du taquin :")
        for move in solution:
            # Pour chaque coup dans la solution, trouve le voisin correspondant
            for neighbor in taquin_instance.get_neighbors():
                if neighbor.move == move:
                    taquin_instance = neighbor # Change l'état du Taquin à l'état du voisin
                    break
        print_taquin(taquin_instance.state) 
    else: 
        print(f"Pas de solution trouvée pour heuristique h{heuristic}.") 
