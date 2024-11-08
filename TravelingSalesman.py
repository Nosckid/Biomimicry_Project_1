import math
import random
import tkinter as tk

# Constant for the number of cities and graphical settings
num_cities = 25
city_scale = 5
road_width = 2
padding = 100


class Node:
    def __init__(self, x, y):
        self.x = x # X-coordinate of the city
        self.y = y # Y-coordinate of the city

    def draw(self, canvas, color='black'):
        # Daw the city on the canvas
        canvas.create_oval(self.x - city_scale, self.y - city_scale,
                           self.x + city_scale, self.y + city_scale, fill=color)


class Edge:
    def __init__(self, a, b):
        self.city_a = a
        self.city_b = b
        self.length = math.hypot(a.x - b.x, a.y - b.y)

    def draw(self, canvas, color='grey', style=(2, 4)):
        canvas.create_line(self.city_a.x,
                           self.city_a.y,
                           self.city_b.x,
                           self.city_b.y,
                           fill=color,
                           width=road_width,
                           dash=style)


class UI(tk.Tk):
    def __init__(self):
        # Initialize the Tkinter window
        super().__init__()
        self.title("Traveling Salesman Problem")

        # Set the window size to full screen
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{width}x{height}+0+0")
        self.state("zoomed")

        # Create a canvas for drawing
        self.canvas = tk.Canvas(self)
        self.canvas.place(x=0, y=0, width=width, height=height)

        # Initialize lists to hold cities and edges
        self.cities = []
        self.edges = []

        # Create a menu bar
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        # Add options to the menu
        salesman_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=salesman_menu, label='Salesman')
        salesman_menu.add_command(label="Generate Cities", command=self.generate_cities_and_edges)
        salesman_menu.add_command(label="Solve with 2-Opt", command=self.solve_with_two_opt)
        salesman_menu.add_command(label="Solve with Genetic Algorithm", command=self.solve_with_genetic)

        self.mainloop()

    def generate_cities_and_edges(self):
        # Clear previous cities and edges
        self.cities.clear()
        self.edges.clear()

        # Generate new cities and edges
        self.create_random_cities()
        self.create_edges_between_cities()
        self.display_cities_and_edges()

    def create_random_cities(self):
        # Create a specified number of random cities
        for _ in range(num_cities):
            x = random.randint(padding, self.winfo_width() - padding)
            y = random.randint(padding, self.winfo_height() - padding)
            city = Node(x, y)
            self.cities.append(city)

    def create_edges_between_cities(self):
        # Create edges between all pairs of cities
        for i in range(len(self.cities)):
            for j in range(i + 1, len(self.cities)):
                edge = Edge(self.cities[i], self.cities[j])
                self.edges.append(edge)

    def display_cities_and_edges(self):
        # Clear the canvas and draw cities and edges
        self.canvas.delete("all")
        for edge in self.edges:
            edge.draw(self.canvas, color='grey', style=(2, 4))
        for city in self.cities:
            city.draw(self.canvas, color='black')

    def solve_with_two_opt(self):
        # Check if cities are available to solve
        if not self.cities:
            return
        self.initialize_tour()
        self.display_current_tour()
        self.perform_two_opt_optimization()

    def initialize_tour(self):
        # Create an initial random tour of cities
        self.tour = list(range(len(self.cities)))
        random.shuffle(self.tour)
        self.best_distance = self.calculate_tour_distance(self.tour)
        self.iteration_i = 1
        self.iteration_k = self.iteration_i + 1

    def calculate_tour_distance(self, tour):
        # Calculate the total distance of the tour
        total_distance = 0
        for i in range(len(tour)):
            city_a = self.cities[tour[i]]
            city_b = self.cities[tour[(i + 1) % len(tour)]]
            distance = math.hypot(city_a.x - city_b.x, city_a.y - city_b.y)
            total_distance += distance
        return total_distance

    def swap_two_opt(self, tour, i, k):
        # Swap the tour segments for the 2-opt optimization
        new_tour = tour[:i] + tour[i:k + 1][::-1] + tour[k + 1:]
        return new_tour

    def perform_two_opt_optimization(self):
        # Perform the 2-opt optimization step
        if self.iteration_i >= len(self.tour) - 1:
            print(f"2-Opt Optimization complete. Final distance: {self.best_distance:.2f}")
            return

        i = self.iteration_i
        k = self.iteration_k
        new_tour = self.swap_two_opt(self.tour, i, k)
        new_distance = self.calculate_tour_distance(new_tour)

        if new_distance < self.best_distance:
            self.tour = new_tour
            self.best_distance = new_distance
            print(f"New best distance: {self.best_distance:.2f}")
            self.iteration_i = 1
            self.iteration_k = self.iteration_i + 1
            self.display_current_tour()
        else:
            self.iteration_k += 1
            if self.iteration_k >= len(self.tour):
                self.iteration_i += 1
                self.iteration_k = self.iteration_i + 1

        self.after(1, self.perform_two_opt_optimization)

    def display_current_tour(self):
        # Clear the canvas and draw the current tour
        self.canvas.delete("all")
        for edge in self.edges:
            edge.draw(self.canvas, color='grey', style=(2, 4))

        for i in range(len(self.tour)):
            city_a = self.cities[self.tour[i]]
            city_b = self.cities[self.tour[(i + 1) % len(self.tour)]]
            self.canvas.create_line(city_a.x, city_a.y, city_b.x, city_b.y, fill='red', width=road_width)

        for city in self.cities:
            city.draw(self.canvas, 'red')

    def solve_with_genetic(self):
        # Check if cities are available to solve
        if not self.cities:
            return
        self.setup_genetic_algorithm()
        self.evolve_population()

    def setup_genetic_algorithm(self):
        # Initialize parameters for the genetic algorithm
        self.population_size = 100
        self.generations = 500
        self.mutation_rate = 0.01
        self.create_initial_population()
        self.generation = 0
        self.best_individual = None
        self.best_distance = float('inf')

    def create_initial_population(self):
        # Create a random initial population
        self.population = []
        for _ in range(self.population_size):
            individual = list(range(len(self.cities)))
            random.shuffle(individual)
            self.population.append(individual)

    def evolve_population(self):
        # Evolve the population over generations
        if self.generation >= self.generations:
            print(f"Genetic Algorithm complete. Final distance: {self.best_distance:.2f}")
            self.tour = self.best_individual
            self.display_current_tour()
            return

        self.generation += 1
        self.evaluate_population()
        self.perform_selection()
        self.perform_crossover()
        self.perform_mutation()
        self.after(1, self.evolve_population)

    def evaluate_population(self):
        # Evaluate the fitness of each individual in the population
        fitness_scores = []
        for individual in self.population:
            distance = self.calculate_tour_distance(individual)
            fitness_scores.append((1 / distance, individual))
            if distance < self.best_distance:
                self.best_distance = distance
                self.best_individual = individual.copy()
                print(f"Generation {self.generation}: New best distance: {self.best_distance:.2f}")
                self.tour = self.best_individual
                self.display_current_tour()

        self.fitness_scores = fitness_scores

    def perform_selection(self):
        # Select individuals for the next generation using roulette wheel selection
        self.population = [ind for _, ind in sorted(self.fitness_scores, reverse=True)]
        total_fitness = sum(score for score, _ in self.fitness_scores)
        probabilities = [score / total_fitness for score, _ in self.fitness_scores]
        cumulative_probabilities = []
        cumulative = 0
        for p in probabilities:
            cumulative += p
            cumulative_probabilities.append(cumulative)

        new_population = []
        for _ in range(self.population_size):
            r = random.random()
            for i, cumulative_probability in enumerate(cumulative_probabilities):
                if r <= cumulative_probability:
                    new_population.append(self.population[i])
                    break
        self.population = new_population

    def perform_crossover(self):
        # Create new individuals through crossover
        new_population = []
        for i in range(0, self.population_size, 2):
            parent1 = self.population[i]
            parent2 = self.population[i + 1] if i + 1 < self.population_size else self.population[0]
            child1, child2 = self.order_crossover(parent1, parent2)
            new_population.extend([child1, child2])
        self.population = new_population

    def order_crossover(self, parent1, parent2):
        # Perform ordered crossover between two parents
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child1 = [None] * size
        child1[start:end + 1] = parent1[start:end + 1]
        self.fill_remaining_genes(child1, parent2)

        child2 = [None] * size
        child2[start:end + 1] = parent2[start:end + 1]
        self.fill_remaining_genes(        child2, parent1)

        return child1, child2

    def fill_remaining_genes(self, child, parent):
        # Fill in the remaining genes in the child that are not already in it
        pointer = 0
        for gene in parent:
            if gene not in child:
                while child[pointer] is not None:  # Find the next available spot in child
                    pointer += 1
                child[pointer] = gene

    def perform_mutation(self):
        # Mutate individuals in the population
        for individual in self.population:
            if random.random() < self.mutation_rate:  # Check if mutation occurs
                i, j = random.sample(range(len(individual)), 2)  # Select two random positions
                individual[i], individual[j] = individual[j], individual[i]  # Swap the positions

# Node and Edge classes should be defined here
class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas, color):
        # Draw the city on the canvas
        radius = 5
        canvas.create_oval(self.x - radius, self.y - radius,
                           self.x + radius, self.y + radius,
                           fill=color)

class Edge:
    def __init__(self, city1, city2):
        self.city1 = city1
        self.city2 = city2

    def draw(self, canvas, color, style=(1, 0)):
        # Draw the edge between two cities
        canvas.create_line(self.city1.x, self.city1.y,
                           self.city2.x, self.city2.y,
                           fill=color, dash=style)

# Constants
num_cities = 10  # Specify the number of cities
padding = 50     # Padding for city generation
road_width = 2   # Width of the road lines

# Run the application
if __name__ == "__main__":
    app = UI()
