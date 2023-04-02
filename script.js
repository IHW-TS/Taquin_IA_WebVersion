const heuristicsData = {
    1: { totalExecutionTime: 0, totalCpuTime: 0, totalStatesExplored: 0, executionCounter: 0 },
    2: { totalExecutionTime: 0, totalCpuTime: 0, totalStatesExplored: 0, executionCounter: 0 },
    3: { totalExecutionTime: 0, totalCpuTime: 0, totalStatesExplored: 0, executionCounter: 0 },
    4: { totalExecutionTime: 0, totalCpuTime: 0, totalStatesExplored: 0, executionCounter: 0 },
    5: { totalExecutionTime: 0, totalCpuTime: 0, totalStatesExplored: 0, executionCounter: 0 },
    6: { totalExecutionTime: 0, totalCpuTime: 0, totalStatesExplored: 0, executionCounter: 0 },
};
let executionCounter = 0;


class Taquin {
    constructor(state, parent = null, move = null, g = 0) {
        this.state = state;
        this.parent = parent;
        this.move = move;
        this.g = g;
    }

    getNeighbors() {
        const neighbors = [];
        const moves = [
            ['N', [-1, 0]],
            ['S', [1, 0]],
            ['E', [0, 1]],
            ['W', [0, -1]],
        ];
        let x, y;

        for (let i = 0; i < this.state.length; i++) {
            const row = this.state[i];
            for (let j = 0; j < row.length; j++) {
                const cell = row[j];
                if (cell === 0) {
                    x = i;
                    y = j;
                    break;
                }
            }
            if (x !== undefined) {
                break;
            }
        }

        for (const [move, [dx, dy]] of moves) {
            const nx = x + dx;
            const ny = y + dy;
            if (
                nx >= 0 &&
                nx < this.state.length &&
                ny >= 0 &&
                ny < this.state[0].length
            ) {
                const newState = this.state.map((row) => row.slice());
                [newState[x][y], newState[nx][ny]] = [newState[nx][ny], newState[x][y]];
                neighbors.push(
                    new Taquin(newState, this, move, this.g + 1)
                );
            }
        }

        return neighbors;
    }

    getDistance(i, j) {
        const [targetX, targetY] = [
            Math.floor((this.state[i][j] - 1) / this.state[0].length),
            (this.state[i][j] - 1) % this.state[0].length,
        ];
        return Math.abs(targetX - i) + Math.abs(targetY - j);
    }

    h(heuristic) {
        if (heuristic === 6) {
            return this.state
                .flatMap((row, i) =>
                    row.map((cell, j) => (cell === 0 ? 0 : this.getDistance(i, j)))
                )
                .reduce((sum, dist) => sum + dist, 0);
        } else {
            const weights = [
                [36, 12, 12, 4, 1, 1, 4, 0],
                [8, 7, 6, 5, 4, 3, 2, 1],
                [8, 7, 6, 5, 3, 2, 4, 1],
            ];
            let pi;
            if (heuristic === 1) {
                pi = weights[0];
            } else if (heuristic === 2 || heuristic === 3) {
                pi = weights[1];
            } else if (heuristic === 4 || heuristic === 5) {
                pi = weights[2];
            }
            const pk =
                heuristic === 1 || heuristic === 3 || heuristic === 5 ? 4 : 1;
            return (
                this.state
                    .flatMap((row, i) =>
                        row.map(
                            (cell, j) =>
                                cell === 0 ? 0 : pi[cell - 1] * this.getDistance(i, j)
                        )
                    )
                    .reduce((sum, dist) => sum + dist, 0) // Somme des distances pondérées
            ) / pk;
        }
    }

    f(heuristic) {
        return this.g + this.h(heuristic);
    }

    compareTo(other) {
        const stateString = JSON.stringify(this.state);
        const otherStateString = JSON.stringify(other.state);
        if (stateString < otherStateString) {
            return -1;
        } else if (stateString > otherStateString) {
            return 1;
        } else {
            return 0;
        }
    }



}
function solveTaquin(initialState, finalState, heuristic) {
    const initialTaquin = new Taquin(initialState);
    const frontier = [[initialTaquin.f(heuristic), initialTaquin]];
    const explored = new Set();
    let numExplored = 0;

    while (frontier.length > 0) {
        frontier.sort(([f1], [f2]) => f1 - f2);
        const [_, current] = frontier.shift();
        if (JSON.stringify(current.state) === JSON.stringify(finalState)) {
            const solution = [];
            let node = current;
            while (node.parent) {
                solution.unshift(node.move);
                node = node.parent;
            }
            return [solution, numExplored];
        }

        explored.add(JSON.stringify(current.state));
        numExplored++;

        for (const neighbor of current.getNeighbors()) {
            if (!explored.has(JSON.stringify(neighbor.state))) {
                frontier.push([neighbor.f(heuristic), neighbor]);
            }
        }
    }

    return [null, numExplored];
}


function generateRandomState(size) {
    const state = Array.from({ length: size * size }, (_, i) => i);
    for (let i = state.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [state[i], state[j]] = [state[j], state[i]];
    }
    return Array.from({ length: size }, (_, i) =>
        state.slice(i * size, (i + 1) * size)
    );
}

function isSolvable(state) {
    let inversions = 0;
    const flattened = state.flat();
    const size = state.length;

    for (let i = 0; i < size * size - 1; i++) {
        for (let j = i + 1; j < size * size; j++) {
            if (flattened[i] && flattened[j] && flattened[i] > flattened[j]) {
                inversions++;
            }
        }
    }

    if (size % 2 === 1) {
        return inversions % 2 === 0;
    } else {
        const blankRow = state.findIndex((row) => row.includes(0));
        if (blankRow % 2 === 0) {
            return inversions % 2 === 1;
        } else {
            return inversions % 2 === 0;
        }
    }
}

function generateStates(size) {
    let initialState;
    do {
        initialState = generateRandomState(size);
    } while (!isSolvable(initialState));

    const finalState = Array.from({ length: size }, (_, i) =>
        Array.from({ length: size }, (_, j) => (i * size + j + 1) % (size * size))
    );
    return [initialState, finalState];
}



function runTaquin(event) {
    event.preventDefault();

    const size = parseInt(document.getElementById("size").value);
    const heuristic = parseInt(document.getElementById("heuristic").value);
    const [initialState, finalState] = generateStates(size);

    printTaquin("initialState", initialState);

    const startTime = performance.now();
    const [solution, numExplored] = solveTaquin(initialState, finalState, heuristic);
    const executionTime = performance.now() - startTime;

    if (solution) {
        executionCounter++;

        // Mettre à jour les totaux pour l'heuristique sélectionnée
        heuristicsData[heuristic].totalExecutionTime += executionTime;
        heuristicsData[heuristic].totalCpuTime += performance.now() - startTime;
        heuristicsData[heuristic].totalStatesExplored += numExplored;
        heuristicsData[heuristic].executionCounter++;

        // Calculer les moyennes pour l'heuristique sélectionnée
        const averageExecutionTime = heuristicsData[heuristic].totalExecutionTime / heuristicsData[heuristic].executionCounter;
        const averageCpuTime = heuristicsData[heuristic].totalCpuTime / heuristicsData[heuristic].executionCounter;
        const averageStatesExplored = heuristicsData[heuristic].totalStatesExplored / heuristicsData[heuristic].executionCounter;

        // Afficher les résultats
        document.getElementById("numExplored").innerText = `${numExplored}`;
        document.getElementById("numMoves").innerText = `${solution.length}`;
        document.getElementById("heuristicSolution").innerText = /*h${heuristic}:*/ `${solution.join(" ")}`;
        document.getElementById("executionTime").innerText = `${executionTime.toFixed(2)} ms`;
        document.getElementById("cpuTime").innerText = `${(performance.now() - startTime).toFixed(2)} ms`;

        // Afficher les moyennes
        document.getElementById("averageExecutionTime").innerText = `${averageExecutionTime.toFixed(2)} ms`;
        document.getElementById("averageCpuTime").innerText = `${averageCpuTime.toFixed(2)} ms`;
        document.getElementById("averageStatesExplored").innerText = `${averageStatesExplored.toFixed(2)}`;

        printTaquin("finalState", finalState);
        updateChart(numExplored, heuristic, executionTime);
    }
}



document.addEventListener("DOMContentLoaded", function () {
    const runButton = document.getElementById("runButton");
    runButton.addEventListener("click", (event) => runTaquin(event)); // Passez l'événement à la fonction runTaquin
});

// fonction pour effet Blackhole 
function setBlackHoleEffect() {
    const emptyCells = document.querySelectorAll(".grid-item[data-empty='true'], .grid-item[data-empty='true'] ~ .grid-item");

    if (emptyCells.length === 0) return;
  
    emptyCells.forEach((emptyCell) => {
      emptyCell.addEventListener("mouseover", () => {
        const parent = emptyCell.parentElement.parentElement;
        const cells = parent.querySelectorAll(".grid-item:not([data-empty='true'])");
        const emptyCellRect = emptyCell.getBoundingClientRect();
  
        cells.forEach((cell) => {
          const cellRect = cell.getBoundingClientRect();
          const dx = emptyCellRect.left - cellRect.left;
          const dy = emptyCellRect.top - cellRect.top;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const factor = Math.min(1, 100 / distance);
  
          cell.style.transform = `translate(${dx * factor}px, ${dy * factor}px) scale(${1 - factor * 0.5})`;
          cell.style.opacity = 1 - factor;
        });
      });
  
      emptyCell.addEventListener("mouseout", () => {
        const parent = emptyCell.parentElement.parentElement;
        const cells = parent.querySelectorAll(".grid-item:not([data-empty='true'])");
  
        cells.forEach((cell) => {
          cell.style.transform = 'translate(0, 0) scale(1)';
          cell.style.opacity = '1';
        });
      });
    });
  }
  
  

// Affiche les différents Etats 
function displayGrid(elementId, state) {
    const container = document.getElementById(elementId);
    container.innerHTML = "";
  
    const grid = document.createElement("div");
    grid.className = "grid";
    container.appendChild(grid);
  
    let cellId = 1;
  
    for (const row of state) {
      const gridRow = document.createElement("div");
      gridRow.className = "grid-row";
      grid.appendChild(gridRow);
  
      for (const cell of row) {
        const gridItem = document.createElement("div");
        gridItem.className = "grid-item";
        gridItem.textContent = cell === 0 ? " " : cell;
        if (cell === 0) {
          gridItem.setAttribute("data-empty", "true");
        } else {
          gridItem.id = `cell${cellId}`;
          cellId++;
        }
        gridRow.appendChild(gridItem);
      }
    }
  }
  
  
  function printTaquin(elementId, state) {
    displayGrid(elementId, state);
    setBlackHoleEffect();
}


document.getElementById("initialStateButton").addEventListener("click", function () {
    toggleVisibility("initialStateContainer");
});

document.getElementById("resultsButton").addEventListener("click", function () {
    toggleVisibility("resultsContainer");
});

document.getElementById("finalStateButton").addEventListener("click", function () {
    toggleVisibility("finalStateContainer");
});

function toggleVisibility(containerId) {
    const container = document.getElementById(containerId);
    container.hidden = !container.hidden;
}


// Affichage du graphique 

let resultChart;

function updateChart(numExplored, heuristic, executionTime) {
    const averageExecutionTime = (heuristicsData[heuristic].totalExecutionTime / heuristicsData[heuristic].executionCounter).toFixed(2);
    const averageStatesExplored = (heuristicsData[heuristic].totalStatesExplored / heuristicsData[heuristic].executionCounter).toFixed(2);
    const averageCpuTime = (heuristicsData[heuristic].totalCpuTime / heuristicsData[heuristic].executionCounter).toFixed(2);
  

    if (!resultChart) {
        const chartElement = document.getElementById("resultChart");


        resultChart = new Chart(chartElement, {
            type: "bar",
            data: {
                labels: ["h1", "h2", "h3", "h4", "h5", "h6"],
                datasets: [
                    {
                        label: " Moyenne Nombre d'états explorés",
                        data: [0, 0, 0, 0, 0, 0],
                        backgroundColor: "rgba(75, 192, 192, 0.2)",
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 1,
                    },
                    {
                        label: "Moyenne Temps d'exécution (ms)",
                        data: [0, 0, 0, 0, 0, 0],
                        backgroundColor: "rgba(255, 99, 132, 0.2)",
                        borderColor: "rgba(255, 99, 132, 1)",
                        borderWidth: 1,
                    },
                    {
                        label: 'Moyenne Temps CPU (ms)',
                        data: [],
                        borderColor: 'rgba(144,238,144,1)',
                        backgroundColor: 'rgba(144,238,144,0.2)',
                        borderWidth: 1,
                    }
                    /*{
                        label: 'Moyenne (ms)',
                        data: [],
                        borderColor: 'rgba(218, 112, 214, 1)',
                        backgroundColor: 'rgba(238, 130, 238, 0.2)',
                        borderWidth: 1,
                    }*/
                    
                    
                ],
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }

   /* resultChart.data.datasets[0].data[heuristic - 1] = numExplored;*/
   resultChart.data.datasets[0].data[heuristic - 1] = averageStatesExplored;
   resultChart.data.datasets[1].data[heuristic - 1] = averageExecutionTime;
   resultChart.data.datasets[2].data[heuristic - 1] = averageCpuTime;
   
   resultChart.update();
   

   
}
