from django.urls import path

from .views import skill_wheel_api, student_recommendations

app_name = "matching"

urlpatterns = [
    path("student/recommendations/", student_recommendations, name="student_recommendations"),
    path("api/skill-wheel/", skill_wheel_api, name="skill_wheel_api"),
]
