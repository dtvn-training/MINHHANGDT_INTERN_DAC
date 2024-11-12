num = 10
print("Integer:", num)

# Float
price = 19.99
print("Float:", price)

# String
name = "Python Programming"
print("String:", name)

# Boolean
is_active = True
print("Boolean:", is_active)

# List (Collection)
colors = ["red", "green", "blue"]
print("List:", colors)

# Tuple (Immutable collection)
coordinates = (10, 20)
print("Tuple:", coordinates)

# Set (Unique collection)
unique_numbers = {1, 2, 3, 3}
print("Set:", unique_numbers)

# Dictionary (Key-Value Pair)
student = {"name": "John", "age": 21}
print("Dictionary:", student)

# Modules and Functions

# Function to add two numbers
def add(a, b):
    return a + b

result = add(5, 7)
print("Function result:", result)

# Working with Files (IO)
# Writing to a file
with open("learn_python\sample.txt", "w") as file:
    file.write("This is a test file.")

# Reading from the file
with open("learn_python\sample.txt", "r") as file:
    content = file.read()
    print("File content:", content)

# OOP: Basic Class Example
class Animal:
    def __init__(self, name, species):
        self.name = name
        self.species = species
    
    def make_sound(self):
        print(f"{self.name} says hello!")

# Creating an object of the Animal class
dog = Animal("Buddy", "Dog")
dog.make_sound()

# Exception Handling: Try-Except Block
try:
    value = int(input("Enter a number: "))
    print("You entered:", value)
except ValueError:
    print("Oops! That's not a valid number.")
