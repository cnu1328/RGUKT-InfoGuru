
import re
from rest_framework import serializers
import uuid


class SignupSerializer(serializers.Serializer):
    """
    Serializer for user signup.
    """
    email = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    def validate_email(self, value):
        """
        Validate the email field.
        Ensures that the provided email is valid.
        """
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        pattern = re.compile(regex)

        if not value:
            raise serializers.ValidationError("Email should not be empty.")

        if not re.search(pattern, value):
            raise serializers.ValidationError("Enter a valid email address.")

        return value

    def validate_password(self, value):
        """
        Validate password complexity.
        Ensures the password contains at least:
        - One uppercase letter
        - One lowercase letter
        - One digit
        - One special character
        - Minimum length of 8 characters
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")

        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.CharField()
    password = serializers.CharField()

    def validate_email(self, value):
        """
        Validate the email field.
        Ensures that the provided email is valid.
        """
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        pattern = re.compile(regex)

        if not value:
            raise serializers.ValidationError("Email should not be empty.")

        if not re.search(pattern, value):
            raise serializers.ValidationError("Enter a valid email address.")

        return value

class UserDataSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(max_length=50, read_only=True)
    avatar = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

