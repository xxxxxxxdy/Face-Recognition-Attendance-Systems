from django.http import JsonResponse
from face_app.models import StudentUser, Teacher, Administrators
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from face_app.models import StudentUser, Teacher, Administrators

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message="Success", code=200):
    return JsonResponse({
        "code": code,
        "message": message,
        "data": data
    },status=code)

def error_response(message="Error", code=400, data=None):
    return JsonResponse({
        "code": code,
        "message": message,
        "data": data
    },status=code)

