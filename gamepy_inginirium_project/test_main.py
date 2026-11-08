from classes import Phone, Student, StudentNew


def main():
    my_phone = Phone()
    print(my_phone.color)
    print(my_phone.battery)
    my_phone.take_photo()
    print(my_phone.battery)

    my_student = Student(grades=[])  # а правильно:   my_student = Student(grades=[])
    my_student.add_grade(3)
    my_student.add_grade(5)
    a = my_student.get_average()
    print(a)
    my_student.add_grade(4)
    my_student.add_grade(3)
    my_student.add_grade(5)
    a = my_student.get_average()
    print(a)

    # Студент_new
    my_student = StudentNew()
    my_student.add_grade(4)
    my_student.add_grade(3)
    my_student.add_grade(6)
    a = my_student.get_average()
    print(a)
