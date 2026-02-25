from models import Student, Classroom

# start top performing student Analytics 
def top_performing_student(classroom_obj):
    if not classroom_obj.list_of_student:
        return "Sorry there are no students in this class currently"
    
    top_student_in_classroom = classroom_obj.list_of_student[0]

    for student in classroom_obj.list_of_student:
        try:
            if student.calculate_average() > top_student_in_classroom.calculate_average():
                top_student_in_classroom = student
        except TypeError:
            print(f" Could not compare student {student.name} due to incomplete data")
            
    return top_student_in_classroom
# end top performing student Analytics

# start lowest performing student Analytics
def lowest_performing_student(classroom_obj):
    if not classroom_obj.list_of_student:
        return "Sorry there are no students in this class currently"
    
    lowest_student_in_classroom = classroom_obj.list_of_student[0]

    for student in classroom_obj.list_of_student:
        try:
            if student.calculate_average() < lowest_student_in_classroom.calculate_average():
                lowest_student_in_classroom = student
        except TypeError:
            print(f"Could not compare student {student.name} due to missing data")
            
    return lowest_student_in_classroom
# end lowest performing student Analytics

# start ranking student Analytics
def ranking_student(classroom_obj):
    if not classroom_obj.list_of_student:
        return "Sorry the class is empty"
    
    temp_list_of_student = classroom_obj.list_of_student[:]
    sorted_list = []

    while len(temp_list_of_student) > 0:
        top_student = temp_list_of_student[0]
        for student in temp_list_of_student:
            try:
                if student.calculate_average() > top_student.calculate_average():
                    top_student = student
            except TypeError:
                print(f"Skipped student ({student.name}) during ranking due to data error")
        
        sorted_list.append(top_student)
        temp_list_of_student.remove(top_student)
        
    return sorted_list
# end ranking student Analytics

# start grade distribution  Analytics
def get_grade_distribution(classroom_obj):
    if not classroom_obj.list_of_student:
        return "The student list is empty"

    distribution = {
        "A+": 0, "A": 0, "B+": 0, "B": 0, 
        "C+": 0, "C": 0, "D+": 0, "D": 0, "F": 0
    }

    for student in classroom_obj.list_of_student:
        average = student.calculate_average()
        grade = student.grade_category(average)
        
        if grade in distribution:
            distribution[grade] += 1
            
    return distribution
# end grade distribution  Analytics

