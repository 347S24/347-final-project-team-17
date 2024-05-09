import datetime
import networkx as nx
import matplotlib.pyplot as plt
import base64
from io import BytesIO

"""
Args:
    curriculums (list): Collection of curriculums that need to be satisfied
    satisfied (list): Collection of courses that have been satisfied
    credit_limit: A semester must not surpass this limit

Returns:
    semesters: A list of semesters that satisfy the curriculums
"""
def generate_course_plan(curriculums, credit_limit):

    requirements = build_requirements(curriculums)
    graph = build_graph(requirements)
    topological_courses = list(nx.topological_sort(graph))

    semesters = generate(graph, topological_courses)
    visualization = generate_image(graph)

    semesters = zip_with_terms(semesters)
    print(semesters)

    return semesters, visualization

"""
Helper function takes a list of semesters, and pairs 
each one with their associated term and year for display.

Returns:
    (term, semester): Semester contains a list of courses
"""
def zip_with_terms(semesters):
    now = datetime.datetime.now()
    terms = []

    month = now.month + 5
    year = now.year

    if month < 8: # current term is Spring
        start_year = year
        terms.append(f"Fall {year}")
    else: # current term is Fall
        start_year = year + 1

    end_year = start_year + 4

    for year in range(start_year, end_year + 1):
        terms.append(f"Spring {year}")
        terms.append(f"Fall {year}")

    result_semesters = []
    for i, semester in enumerate(semesters):
        result_semesters += [(terms[i], semester)]
    print(result_semesters)
    return result_semesters

"""
Given a list of courses, return as a graph of requirements.
This will include prerequisites not part of the original list.
"""
def build_graph(course_list):
    graph = nx.DiGraph()
    courses = course_list.copy()
    while courses:
        selected = courses.pop()
        graph.add_node(selected.code, credits=selected.credits)

        for prerequisite in selected.prerequisites.all():
            graph.add_edge(prerequisite.code, selected.code)
            courses.add(prerequisite)
        for corequisite in selected.corequisites.all():
            graph.add_edge(corequisite.code, selected.code)
            courses.add(corequisite)

    return graph

"""
Given a list of curriculums, join them as a single set of 
requirements which must be satisfied.
"""
def build_requirements(curriculums) -> set:
    requirements = set()
    for curriculum in curriculums.all():
        for requirement in curriculum.requirements.all():
            requirements |= requirement.get_satisfiable_subset()
    return requirements

"""
Generation logic goes here.

Given the graph and a topological sort of the graph,
return a list of semesters that satisfy all requirements.
"""
def generate(graph, topological_courses):
    semesters = []
    cur_semester = []
    cur_semester_credits = 0
    credit_limit = 16
    taken_courses = set()

    # Each iteration is one semester being filled
    while topological_courses:
        overflow = False

        # Check each course to see if it can be added to the semester
        for course in topological_courses.copy():

            # Skip if already taken
            if course in taken_courses:
                topological_courses.remove(course)
                continue

            # Check if prerequisites are satisfied, skip if not
            satisfied = True
            for prerequisite in list(graph.predecessors(course)):
                if prerequisite not in taken_courses or prerequisite in cur_semester:
                    satisfied = False
                    break

            if not satisfied:
                continue # Skip

            # Add the course to student plan
            # If adding the course will surpass credit limit, start a new semester. Otherwise, add it.
            if cur_semester_credits + graph.nodes[course]['credits'] > credit_limit:
                overflow = True
                semesters += [cur_semester]
                cur_semester = [course]
                cur_semester_credits = graph.nodes[course]['credits']
                topological_courses.remove(course)
                taken_courses.add(course)
                break
            else:
                cur_semester += [course]
                cur_semester_credits += graph.nodes[course]['credits']
                topological_courses.remove(course)
                taken_courses.add(course)

        # Start new semester now that we have exhausted all courses
        if not overflow:
            semesters += [cur_semester]
            cur_semester = []
            cur_semester_credits = 0
            
    return semesters

"""
Given a graph, generate a base64 raw image representation that may be displayed.
"""
def generate_image(graph):
    graph_layout = nx.spring_layout(graph,  k=3, iterations=500)
    plt.figure(figsize=(9, 7))
    nx.draw(graph, graph_layout, with_labels=True, node_color='skyblue', node_size=1200, edge_color='black', linewidths=3, font_size=9)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    image = image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return image