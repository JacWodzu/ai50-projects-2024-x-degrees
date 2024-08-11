import csv
import sys

from util import Node
from collections import deque

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

class QueueFrontier:
    def __init__(self):
        self.frontier = deque()

    def add_node(self, node):
        self.frontier.append(node)

    def remove_node(self):
        if self.empty():
            raise Exception("frontier is empty")
        else:
            return self.frontier.popleft()

    def empty(self):
        return len(self.frontier) == 0

class Node:
    def __init__(self, action=None, state=None, parent=None):
        self.action = action
        self.state = state
        self.parent = parent

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(fr"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(fr"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(fr"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if row["person_id"] in people and row["movie_id"] in movies:
                    people[row["person_id"]]["movies"].add(row["movie_id"])
                    movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Source person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Target person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    frontier = QueueFrontier()
    frontier.add_node(Node(None, source))  # Corrected initialization

    explored = set()

    while True:
        if frontier.empty():
            return None  # No path found

        current = frontier.remove_node()
        explored.add(current.state)

        if current.state == target:
            path = []
            while current.parent is not None:
                path.append(current.action)
                current = current.parent
            path.reverse()
            return path

        for action, neighbor in neighbors_for_person(current.state).items():
            if neighbor not in explored:
                child = Node(action, neighbor)
                child.parent = current
                frontier.add_node(child)

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
            else:
                return None
        except ValueError:
            return None
    else:
        return person_ids[0]

def neighbors_for_person(person_id):
    """
    Returns a dictionary mapping actions to person_ids for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = {}
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors[(movie_id, person_id)] = person_id
    return neighbors

if __name__ == "__main__":
    main()