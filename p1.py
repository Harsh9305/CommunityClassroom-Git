# Define a function to calculate the average grade
def calculate_average(grades):
    return sum(grades) / len(grades)

# List of student grades
student_grades = [85, 92, 78, 90, 88]

# Calculate the average grade
average_grade = calculate_average(student_grades)

# Write the result to a text file
with open("average_grade.txt", "w") as file:
    file.write(f"The average grade of the students is: {average_grade:.2f}")

print("The average grade has been written to average_grade.txt")
