import numpy as np


class Phone:
    color = "black"
    battery = 100

    def take_photo(self):
        print("Фото сделано!")
        self.battery -= 5
        print(f"осталось баттареи: {self.battery}")
        if self.battery <= 20:
            print("Заряд кончается!")


# СНИЗУ класс, который КОНСТРУИРУЕТСЯ требуя grades сразу
class Student:
    def __init__(self, grades):
        self.grades = list()
        self.name = "George"
        self.age = 27

    def add_grade(self, grade):
        self.grades.append(grade)

    def get_average(self):
        average = np.mean(self.grades)
        return average


class StudentNew:
    grades = list()
    name = "George"
    age = 27

    def add_grade(self, grade):
        self.grades.append(grade)

    def get_average(self):
        average = np.mean(self.grades)
        return average
