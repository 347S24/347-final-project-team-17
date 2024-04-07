from django.utils import timezone
import PyPDF2
import re

def get_graduation_years():
    current_year = timezone.now().year
    return [(year, str(year)) for year in range(current_year, current_year + 8)]

# Returns a list of (code, credits, grade) tuples from the provided transcript.
def extract_course_info(file):

    # Parses course info from transcript line of following format: 
    # "{course code} {course name} {attempted credits} {earned credits} {grade} {gpa points}"
    def parse_course(line):
        if re.match(class_pattern, line):

            course_num = re.search(course_num_pattern, line).group()
            grade_info = re.findall(grade_info_pattern, line)
            grade = re.search(grade_pattern, line)

            if grade:
                grade = grade.group()

            return course_num, int(grade_info[0][0]), grade
        return None

    # Open file in PyPDF2
    reader = PyPDF2.PdfReader(file)
    classes = []

    class_pattern = re.compile(r'[A-Z]{2,5}\s(\d{3}|O{3}).*') # Determine if line is a course listing or some other transcript line
    course_num_pattern = re.compile(r'[A-Z]{2,5}\s(\d{3}|O{3})') # Match courses numbers
    grade_info_pattern = re.compile(r'\d{1,2}\.\d{2,3}') # Match credit hours
    grade_pattern = re.compile(r'(?<=\b\d\.\d\d)[A-Z\-+]*(?=\d+\.\d+\b)') # Match grade

    # Iterate through each page of the PDF
    for page_num in range(len(reader.pages)):

        # Extract text from the page
        page_text = reader.pages[page_num].extract_text(space_width=2)
        lines = page_text.split('\n')

        # Iterate through each line
        for line in lines:
            result = parse_course(line)
            if result:
                classes += [result]
        
    return classes

            