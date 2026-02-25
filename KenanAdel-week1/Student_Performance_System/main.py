from models import Student, Classroom
import utils
import analytics

def draw_line():
    print("--------------------------------------------------" )

def main_menu():
    print("\n" + "**************************************************")
    print("      STUDENT PERFORMANCE ANALYZER ")
    print("**************************************************")
    print(" 1- Add New Student")
    print(" 2- Update Student Information")
    print(" 3- View All Students")
    print(" 4- Search For Student By Id")
    print(" 5- Delete Student")
    print(" 6- Class Analycies")
    print(" 7- Student Rankings")
    print(" 8- Pass and Fail Students")
    print(" 9- Grade Distribution")
    print(" 10- Save and Exit")
    print("**************************************************")

def main():
    my_classroom = Classroom()

    utils.load_students_from_csv(my_classroom)
    
    while True:
        utils.clear()  
        main_menu()
        
        choice = utils.get_number(" ==> Select an option (1-10): ")
        
        if choice == 1:
            print("\n ==> Adding New Student")
            name = utils.get_name("Enter Name: ")
            
            student_id = utils.get_unique_id("Enter ID: ", my_classroom)
            
            valid_grades = utils.get_valid_grades_list("Enter Grades (separated by spaces): ")
            
            new_student = Student(name, student_id, valid_grades)
            msg = my_classroom.add_student(new_student)
            
            print(f" ==> {msg}")
            input("\nPress Enter to return to menu...")

        elif choice == 2:
            utils.handle_student_update(my_classroom)
            input("\nPress Enter to return to menu...")

        elif choice == 3:
            utils.display_all_students(my_classroom)
            input("\nPress Enter to return to menu...")

        elif choice == 4:
            student_id = utils.get_number("Enter Student ID to search: ")
            student = my_classroom.search_student(student_id)
            
            if student:
                avg = student.calculate_average()
                print(f"\n --> Student Found:")
                print(f"    Name:  {student.name}")
                print(f"    ID:    {student.student_id}")
                print(f"    Avg:   {avg:.2f}")
                print(f"    Grade: {student.grade_category(avg)}")
            else:
                print(" ==> Student not found")
                
            input("\nPress Enter to return to menu...")

        elif choice == 5:
            student_id = utils.get_number("Enter Student ID to delete: ")
            result = my_classroom.remove_student(student_id)
            print(f"--> {result}")
            input("\nPress Enter to return to menu...")

        elif choice == 6:
            utils.display_class_summary(my_classroom)
            input("\nPress Enter to return to menu...")

        elif choice == 7:
            utils.display_rankings(my_classroom)
            input("\nPress Enter to return to menu...")

        elif choice == 8:
            utils.show_pass_fail_report(my_classroom)
            input("\nPress Enter to return to menu...")

        elif choice == 9:
            utils.display_grade_distribution(my_classroom)
            input("\nPress Enter to return to menu...")

        elif choice == 10:
            utils.save_students_to_csv(my_classroom)
            print("\n See You Later")
            break

        else:
            print(" ==> Invalid choice Please select from 1 to 10")
            input("Press Enter to try again...")

if __name__ == "__main__":
    main()