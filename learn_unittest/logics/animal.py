class Dog:
    # Initializer / Instance Attributes
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def description(self):
        file_name = 'german_dog.txt'
        infor = "{} is {} years old".format(self.name, self.age)
        with open(file_name, 'w') as f:
            f.write(infor)
        return infor

    def speak(self, sound):
        return "{} says {}".format(self.name, sound)