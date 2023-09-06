import sqlite3
import re


conn = sqlite3.connect("domains.db")
cursor = conn.cursor()


cursor.execute("SELECT DISTINCT project_id FROM domains")
project_ids = cursor.fetchall()


def generate_regex(components):
    regex_pattern = ""
    for component in components:
        if component == "*":
            regex_pattern += "[^.]*\\."
        else:
            regex_pattern += re.escape(component) + "\\."
    return regex_pattern[:-1]


for project_id in project_ids:
    project_id = project_id[0]

    cursor.execute("SELECT name FROM domains WHERE project_id=?", (project_id,))
    domains = cursor.fetchall()

    components_list = []
    for domain in domains:
        components = domain[0].split(".")
        components_list.append(components)

    common_patterns = []
    for i in range(len(components_list)):
        for j in range(i + 1, len(components_list)):
            common_pattern = []
            for c1, c2 in zip(components_list[i], components_list[j]):
                if c1 == c2:
                    common_pattern.append(c1)
                else:
                    common_pattern.append("*")
            common_patterns.append(common_pattern)

    unique_regex_patterns = set()
    for pattern in common_patterns:
        regex_pattern = generate_regex(pattern)
        unique_regex_patterns.add(regex_pattern)

    for regex_pattern in unique_regex_patterns:
        cursor.execute("INSERT INTO rules (regexp, project_id) VALUES (?, ?)",
                       (regex_pattern, project_id))

conn.commit()
conn.close()
