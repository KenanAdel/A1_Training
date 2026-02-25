# start class Student
class Student:
    count = 0
    def __init__(self, name, student_id, grades):
        self.name = name
        self.student_id = student_id
        self.__grades = grades
        Student.count += 1

    @staticmethod
    def is_valid_grade(grade):
        if 0 <= grade <= 100:
            return True
        else:
            print(f" --> Grade {grade} Must be between 0 and 100")
            return False

    @classmethod
    def total_students(cls):
        return f"Total Registered Students: {cls.count}"

    def get_grades(self):
        return self.__grades
    
    def set_grades(self, new_grades):
        self.__grades = new_grades

    def calculate_average(self):
        try:
            Grades_Sum = sum(self.__grades)
            Grades_Len = len(self.__grades)
            Grades_average = Grades_Sum / Grades_Len
        except ZeroDivisionError:
            return f"No grades available for this student {self.name}"

        return Grades_average

    def grade_category(self, Grades_average):
        try:
            if 95 <= Grades_average <= 100:
                return "A+"
            elif 90 <= Grades_average < 95:
                return "A"
            elif 85 <= Grades_average < 90:
                return "B+"
            elif 80 <= Grades_average < 85:
                return "B"
            elif 75 <= Grades_average < 80:
                return "C+"
            elif 70 <= Grades_average < 75:
                return "C"
            elif 65 <= Grades_average < 70:
                return "D+"
            elif 60 <= Grades_average < 65:
                return "D"
            elif 0 <= Grades_average < 60:
                return "F"
            else:
                return "Invalid Grade Range"
        except TypeError:
            return "Cannot calculate grade category"
# end class Student

# start class Classroom
class Classroom:
    def __init__(self):
        self.list_of_student = []

    def add_student(self, student):
        self.list_of_student.append(student)
        return "Student added successfully"
    
    def remove_student(self, student_id):
        for student in self.list_of_student:
            if str(student.student_id) == str(student_id):
                self.list_of_student.remove(student)
                Student.count -= 1 
                return f"Student {student.name} (ID: {student_id}) removed successfully"
        return "--> Student not found"

    def search_student(self, student_id):
        for student in self.list_of_student:
            if str(student.student_id) == str(student_id):
                return student  
        return None  
    
    def calculate_classroom_average(self):
        total_sum = 0
        count = 0
        
        for student in self.list_of_student:
            student_avg = student.calculate_average()
            try:
                total_sum += student_avg
                count += 1
            except TypeError:
                print(f"Student ({student.name}) excluded from average calculation")

        if count == 0:
            return "No students with valid grades in this class"
            
        return total_sum / count

# end class Classroom