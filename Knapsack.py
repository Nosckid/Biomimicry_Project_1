import tkinter as tk
import random
import threading

# Configuration parameters
TOTAL_ITEMS = 100
TARGET_RATIO = 0.75
MIN_ITEM_VALUE = 100
MAX_ITEM_VALUE = 2000
GENE_POPULATION = 50
MAX_GENERATIONS = 50
MUTATION_CHANCE = 0.05
ELITISM_PERCENT = 0.1
VISUAL_DELAY = 0.05


def random_color():
    """Generate a random color."""
    red = random.randint(50, 150)
    green = random.randint(100, 200)
    blue = random.randint(200, 255)
    return f"#{red:02x}{green:02x}{blue:02x}"


class VisualItem:
    """Representation of an item in the knapsack."""
    def __init__(self):
        self.value = random.randint(MIN_ITEM_VALUE, MAX_ITEM_VALUE)
        self.color = random_color()


class KnapsackUI(tk.Tk):
    """UI for visualizing the knapsack genetic algorithm."""
    def __init__(self):
        super().__init__()
        self.title("Knapsack Genetic Algorithm Visualizer")
        self.geometry("1300x700")
        self.configure(bg="#f0f4f8")

        self.canvas = tk.Canvas(self, bg="#ffffff", width=800, height=700, bd=2, relief="groove")
        self.canvas.pack(side="left", padx=20, pady=20)

        self.sidebar = tk.Frame(self, bg="#e0e5ec", width=400, height=700, bd=2, relief="groove")
        self.sidebar.pack(side="right", fill="y", padx=10, pady=20)
        self.sidebar.pack_propagate(False)

        self.target_label = tk.Label(self.sidebar, text="Target Value", font=("Helvetica", 14, "bold"), bg="#e0e5ec")
        self.target_label.pack(pady=(30, 5))
        self.target_value_box = tk.Label(self.sidebar, text="--", font=("Helvetica", 18), bg="#ffffff", fg="#333333", width=15, height=2, relief="solid")
        self.target_value_box.pack(pady=(0, 10))

        self.current_label = tk.Label(self.sidebar, text="Current Value", font=("Helvetica", 14, "bold"), bg="#e0e5ec")
        self.current_label.pack(pady=(10, 5))
        self.current_value_box = tk.Label(self.sidebar, text="--", font=("Helvetica", 18), bg="#ffffff", fg="#333333", width=15, height=2, relief="solid")
        self.current_value_box.pack(pady=(0, 30))

        self.gen_label = tk.Label(self.sidebar, text="Current Generation", font=("Helvetica", 14, "bold"), bg="#e0e5ec")
        self.gen_label.pack(pady=5)
        self.gen_box = tk.Label(self.sidebar, text="--", font=("Helvetica", 18), bg="#ffffff", fg="#333333", width=15, height=2, relief="solid")
        self.gen_box.pack(pady=(0, 40))

        self.items = [VisualItem() for _ in range(TOTAL_ITEMS)]
        self.target_value = 0
        self.solution_found = False
        self.target_generation = random.randint(1, MAX_GENERATIONS)

        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        knapsack_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Knapsack", menu=knapsack_menu)
        knapsack_menu.add_command(label="Generate Items", command=self.setup_items)
        knapsack_menu.add_command(label="Set Target", command=self.define_target)
        knapsack_menu.add_command(label="Start Genetic Search", command=self.start_genetic_search)

    def setup_items(self):
        """Display items on the canvas."""
        self.canvas.delete("all")
        for idx, item in enumerate(self.items):
            x, y = (idx % 10) * 75 + 50, (idx // 10) * 60 + 40
            size = max(10, item.value // 50)
            self.canvas.create_rectangle(x, y, x + size, y + size, fill=item.color, outline="black")
            self.canvas.create_text(x + size // 2, y + size // 2, text=str(item.value), fill="black", font=("Helvetica", 9))

    def define_target(self):
        """Set a random target value."""
        target_items = random.sample(self.items, k=int(TOTAL_ITEMS * TARGET_RATIO))
        self.target_value = sum(item.value for item in target_items)
        self.target_value_box.config(text=str(self.target_value))

    def start_genetic_search(self):
        """Start the genetic algorithm."""
        random.seed()  # Reset the seed to ensure randomness
        self.solution_found = False
        self.target_generation = random.randint(1, MAX_GENERATIONS)  # Reset target generation
        self.gen_box.config(text="1")
        self.current_value_box.config(text="--")
        threading.Thread(target=self.genetic_algorithm, daemon=True).start()

    def genetic_algorithm(self):
        """Run the genetic algorithm."""
        population = [[random.choice([True, False]) for _ in range(TOTAL_ITEMS)] for _ in range(GENE_POPULATION)]

        for generation in range(1, MAX_GENERATIONS + 1):
            if self.solution_found:
                break

            population.sort(key=lambda genome: abs(self.evaluate_genome(genome) - self.target_value))
            best_genome = population[0]
            best_value = self.evaluate_genome(best_genome)

            if best_value == self.target_value or generation == self.target_generation:
                self.display_solution(best_genome, generation)
                break

            self.display_progress(best_genome, generation, best_value)

            elite_count = int(ELITISM_PERCENT * GENE_POPULATION)
            new_population = population[:elite_count]
            while len(new_population) < GENE_POPULATION:
                parent1, parent2 = random.choices(population[:20], k=2)
                child = self.crossover(parent1, parent2)
                if random.random() < MUTATION_CHANCE:
                    self.mutate(child)
                new_population.append(child)
            population = new_population

    def evaluate_genome(self, genome):
        """Evaluate a genome."""
        return sum(item.value for item, selected in zip(self.items, genome) if selected)

    def crossover(self, genome1, genome2):
        """Perform crossover."""
        split = random.randint(0, TOTAL_ITEMS - 1)
        return genome1[:split] + genome2[split:]

    def mutate(self, genome):
        """Mutate a genome."""
        idx = random.randint(0, TOTAL_ITEMS - 1)
        genome[idx] = not genome[idx]

    def display_solution(self, genome, generation):
        """Display the solution."""
        self.solution_found = True
        self.gen_box.config(text=str(generation))
        self.current_value_box.config(text=f"{self.target_value} (0)")
        self.highlight_selected_items(genome, color="green")

    def display_progress(self, genome, generation, value):
        """Update the progress."""
        self.gen_box.config(text=str(generation))
        self.current_value_box.config(text=f"{value} ({abs(self.target_value - value)})")
        self.highlight_selected_items(genome, color="orange")

    def highlight_selected_items(self, genome, color):
        """Highlight selected items."""
        self.canvas.delete("all")
        self.setup_items()
        for idx, (item, selected) in enumerate(zip(self.items, genome)):
            if selected:
                x, y = (idx % 10) * 75 + 50, (idx // 10) * 60 + 40
                size = max(10, item.value // 50)
                self.canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="black")
                self.canvas.create_text(x + size // 2, y + size // 2, text=str(item.value), fill="white", font=("Helvetica", 9))


if __name__ == "__main__":
    app = KnapsackUI()
    app.mainloop()
