from models import Student, Classroom
import analytics
import os
###############################################################################
# start Load students 
def load_students_from_csv(classroom_obj):
    try:
        file = open("data.csv", "r")
        lines = file.readlines() 
        file.close()

        for line in lines:
            if line.startswith("Name"):
                continue

            parts = line.strip().split(",") 
            if len(parts) < 3: 
                continue 
            
            student_name = parts[0]
            student_id = parts[1]
            grades_text = parts[2]
            
            student_grades = []
            for d in grades_text.split(): 
                student_grades.append(float(d))

            new_s = Student(student_name, student_id, student_grades)
            classroom_obj.add_student(new_s)
        
        print("Data loaded successfully")
    except FileNotFoundError:
        print("No previous data found")
    except Exception as e:
        print(f"error while loading: {e}")
# end Load students 

# start save students 
def save_students_to_csv(classroom_obj):
    try:
        file = open("data.csv", "w")
        file.write("Name,ID,Grades\n")
        
        for student in classroom_obj.list_of_student:
            grades_str = ""
            for grade in student.get_grades():
                grades_str = grades_str + str(grade) + " "
            
            line = line = f"{student.name},{student.student_id},{grades_str.strip()}"
            file.write(line + "\n")
            
        file.close()
        print("Data saved successfully to data.csv")
    except Exception as e:
        print(f"Save failed! The file might be open in another program... Error: {e}")
# end save students 

################################################################################
# start Helper and validation functions 
def get_number(msg):
    while True:
        val = input(msg)
        if val.isdigit():
            return int(val)
        else:
            print("Please enter numbers only")

def get_name(msg):
    while True:
        name = input(msg).strip()
        if not name:
            print("Name cannot be empty")
        elif name.isdigit():
            print("Name cannot be numbers only")
        else:
            return name

def get_valid_grades_list(msg):
    while True:
        grades_input = input(msg).strip()
        if not grades_input:
            print(" --> Grades cannot be empty")
            continue
            
        raw_list = grades_input.split()
        valid_grades = []
        is_all_correct = True
        
        for item in raw_list:
            try:
                num = float(item)
                if Student.is_valid_grade(num):
                    valid_grades.append(num)
                else:
                    is_all_correct = False
                    break
            except ValueError:
                print(f" --> '{item}' is not a valid number")
                is_all_correct = False
                break
        
        if is_all_correct and valid_grades:
            return valid_grades
            
        print(" --> Please re-enter the grades correctly")

def get_unique_id(msg, classroom):
    while True:
        student_id = get_number(msg)
        existing_student = classroom.search_student(student_id)
        if existing_student:
            print(f" --> ID '{student_id}' is already taken by {existing_student.name}.")
            continue 
            
        return student_id 
    
def handle_student_update(classroom):
    print("\n--- UPDATE STUDENT INFORMATION ---")
    search_id = get_number("Enter Student ID to update: ")
    
    student = classroom.search_student(search_id)
    
    if not student:
        print("--> Student not found")
        return 

    print(f"--> Found: {student.name}")
    print("What would you like to update?")
    print(" 1. Student Name")
    print(" 2. Student Grades")
    print(" 3. Both (Name and Grades)")
    
    sub_choice = input("Enter your choice (1-3): ")
    
    if sub_choice == '1':
        student.name = get_name("Enter New Name: ")
        print("--> Name updated successfully")
        
    elif sub_choice == '2':
        new_grades = get_valid_grades_list("Enter New Grades: ")
        student.set_grades(new_grades)
        print("--> Grades updated successfully")
        
    elif sub_choice == '3':
        student.name = get_name("Enter New Name: ")
        new_grades = get_valid_grades_list("Enter New Grades: ")
        student.set_grades(new_grades)
        print("--> Name and Grades updated successfully")
    else:
        print("--> Invalid choice Update cancelled")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
# end Helper and validation functions 

################################################################################

# start Helper functions to make main clear
def show_pass_fail_report(classroom, pass_mark=50):
    print("\n--- PASS / FAIL STATUS ---")
    pass_list = []
    fail_list = []
    
    for student in classroom.list_of_student:
        avg = student.calculate_average()
        if avg >= pass_mark:
            pass_list.append(student)
        else:
            fail_list.append(student)

    print(f"\n PASSING ({len(pass_list)}):")
    for s in pass_list:
        print(f" - {s.name:<15} (Avg: {s.calculate_average():.2f})")

    print(f"\n FAILING ({len(fail_list)}):")
    for s in fail_list:
        print(f" - {s.name:<15} (Avg: {s.calculate_average():.2f})")

def display_class_summary(classroom):
    print("\n--- CLASS STATISTICS ---")
    
    if classroom.list_of_student:
        top = analytics.top_performing_student(classroom)
        low = analytics.lowest_performing_student(classroom)
        cls_avg = classroom.calculate_classroom_average()
        
        print(f" Best Student: {top.name} ({top.calculate_average():.2f})")
        print(f" Last Student: {low.name} ({low.calculate_average():.2f})")
        print(f" Class Mean Score: {cls_avg:.2f}")
    else:
        print(" ---> No students found to analyze.")

def display_grade_distribution(classroom):
    print("\n--- GRADE DISTRIBUTION ---")
    
    if classroom.list_of_student:
        dist = analytics.get_grade_distribution(classroom)
        for letter, count in dist.items(): 
            print(f" Grade {letter}: {count} student(s)")
    else:
        print(" ---> No students found to analyze.")

def display_all_students(classroom):
    print("\n--- STUDENT LIST ---")
    print(f" Total Students: {Student.total_students()}")
    print("-" * 50)
    
    students = classroom.list_of_student
    if not students:
        print("The classroom is empty.")
    else:
        print(f"{'ID':<10} | {'Name':<15} | {'Avg':<8} | {'Grade'}")
        print("-" * 50)
        for s in students:
            avg = s.calculate_average()
            cat = s.grade_category(avg)
            print(f"{s.student_id:<10} | {s.name:<15} | {avg:<8.2f} | {cat}")
    print("-" * 50)

def display_rankings(classroom):
    print("\n--- RANKING (High to Low) ---")
    ranked = analytics.ranking_student(classroom)
    
    if classroom.list_of_student:
        rank_number = 1 
        for s in ranked:
            print(f"{rank_number}. {s.name:<15} -> Avg: {s.calculate_average():.2f}")
            rank_number += 1  
    else:
        print("No students to rank.")
# end Helper functions to make main clear

###############################################################################