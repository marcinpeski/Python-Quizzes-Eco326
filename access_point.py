# Import the Canvas class
from canvasapi import Canvas

# Canvas API URL
API_URL = "https://q.utoronto.ca"
# Canvas API key
API_KEY = "11834~Bi5SS3eXPaR04wz7UcwHvr0WixajNTFFvQvrWhE9COhupnj0ToZUjlcY0fwComgF"

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

# Grab course 123456
course = canvas.get_course(311156)

# Access the course's name
print(course.name)

import requests

# Your Canvas API URL
canvas_url = "https://q.utoronto.ca/api/v1/"

# Your Access Token
access_token = "11834~Bi5SS3eXPaR04wz7UcwHvr0WixajNTFFvQvrWhE9COhupnj0ToZUjlcY0fwComgF"

# Headers for Authentication
headers = {
    "Authorization": f"Bearer {access_token}"
}

course_id = "311156"
response = requests.get(f"{canvas_url}/courses/{course_id}/students/submissions", headers=headers)
grades = response.json()

