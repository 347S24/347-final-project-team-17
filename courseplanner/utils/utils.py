from django.utils import timezone
import PyPDF2
import re
# from openpyxl import Workbook
# from openpyxl.styles import Alignment, Font

def get_graduation_years():
    current_year = timezone.now().year
    return [(year, str(year)) for year in range(current_year, current_year + 8)]


# Returns a list of (code, credits, grade) tuples from the provided transcript.
def extract_course_info(file):

    # Parses course info from transcript line of following format: 
    # "{course code} {course name} {attempted credits} {earned credits} {grade} {gpa points}"
    def parse_course(line, semester, year):
        if re.match(class_pattern, line):

            course_num = re.search(course_num_pattern, line).group()
            grade_info = re.findall(grade_info_pattern, line)
            grade = re.search(grade_pattern, line)

            if grade:
                grade = grade.group()

            return year, semester, course_num, int(grade_info[0][0]), grade
        return None

    # Open file in PyPDF2
    reader = PyPDF2.PdfReader(file)
    classes = []

    class_pattern = re.compile(r'[A-Z]{2,5}\s(\d{3}|O{3}).*') # Determine if line is a course listing or some other transcript line
    course_num_pattern = re.compile(r'[A-Z]{2,5}\s(\d{3}|O{3})') # Match courses numbers
    grade_info_pattern = re.compile(r'\d{1,2}\.\d{2,3}') # Match credit hours
    grade_pattern = re.compile(r'(?<=\b\d\.\d\d)[A-Z\-+]*(?=\d+\.\d+\b)') # Match grade
    semester_pattern = re.compile(r'(Spring|Summer|Fall|Winter) (Semester|Session) (\d{4})') # Match semester and year

    curr_semester = None
    curr_year = None
    
    # Iterate through each page of the PDF
    for page_num in range(len(reader.pages)):

        # Extract text from the page
        page_text = reader.pages[page_num].extract_text(space_width=2)
        lines = page_text.split('\n')

        # Iterate through each line
        for line in lines:
            # Check for semester information
            semester_match = re.match(semester_pattern, line)
            if semester_match:
                curr_semester, _, curr_year = semester_match.groups()
                continue

            # Parse course information
            result = parse_course(line, curr_semester, curr_year)
            if result:
                classes += [result]
        
    return classes


# def create_course_plan(filename, name, email, course_data):
    
#     # Generates an Excel file that fills in the cells based on tuples of semester, year, course code, credits, grades.

#     # :param filename: Name of the Excel file to be generated.
#     # :param name: Name of the user.
#     # :param email: Email of the user.
#     # :param course_data: List of tuples with semester, year, course code, and credits.
    
#     # Create a new Excel workbook and select the active worksheet
#     workbook = Workbook()
#     sheet = workbook.active
#     sheet.title = "Course Plan"

#     # Style settings
#     title_font = Font(size=14, bold=True)
#     header_font = Font(size=12, bold=True)
#     centered_alignment = Alignment(horizontal="center", vertical="center")

#     # Add user details at the top
#     sheet["A1"] = "Course Planner"
#     sheet["A1"].font = title_font
#     sheet.merge_cells("A1:D1")

#     sheet["A2"] = f"Name: {name}"
#     sheet["A3"] = f"Email: {email}"

#     # Define headers for the course plan
#     headers = ["Semester", "Year", "Course Code", "Credits"]
#     for col, header in enumerate(headers, start=1):
#         cell = sheet.cell(row=5, column=col, value=header)
#         cell.font = header_font
#         cell.alignment = centered_alignment

#     # Add course data
#     for row, (semester, year, course_code, credits) in enumerate(course_data, start=6):
#         sheet.cell(row=row, column=1, value=semester).alignment = centered_alignment
#         sheet.cell(row=row, column=2, value=year).alignment = centered_alignment
#         sheet.cell(row=row, column=3, value=course_code).alignment = centered_alignment
#         sheet.cell(row=row, column=4, value=credits).alignment = centered_alignment

#     # Adjust column widths
#     column_widths = [15, 10, 15, 10]
#     for col_num, width in enumerate(column_widths, start=1):
#         sheet.column_dimensions[chr(64 + col_num)].width = width

#     # Save the Excel file
#     workbook.save(filename)
#     print(f"Excel file '{filename}' created successfully!")
