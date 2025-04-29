import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'
AUTH_URL = f'{BASE_URL}/auth'

def get_auth_token():
    """Hämta JWT-token för autentisering"""
    response = requests.post(
        f'{AUTH_URL}/login',
        json={
            'username': 'testuser',
            'password': 'testpassword'
        }
    )
    return response.json()['access_token']

def test_register():
    """Testa att registrera en ny användare"""
    response = requests.post(
        f'{AUTH_URL}/register',
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        }
    )
    print("Registrera användare:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}")

def test_create_todo(token):
    """Testa att skapa en ny todo med autentisering"""
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f'{BASE_URL}/todos',
        headers=headers,
        json={
            'title': 'Test Todo',
            'description': 'Detta är en test todo',
            'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
            'category': 'Test'
        }
    )
    print("Skapa todo:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}")
    return response.json()

def test_get_all_todos(token):
    """Hämta alla todos"""
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/todos', headers=headers)
    print("Hämta alla todos:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}")

def test_get_sorted_todos():
    """Hämta todos sorterade efter deadline"""
    response = requests.get(f'{BASE_URL}/todos/sort/deadline')
    print("Hämta todos sorterade efter deadline:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}")

def test_get_todos_by_category():
    """Hämta todos efter kategori"""
    response = requests.get(f'{BASE_URL}/todos/category/Studier')
    print("Hämta todos efter kategori:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}")

if __name__ == '__main__':
    # Testa alla endpoints
    test_register()
    token = get_auth_token()
    test_create_todo(token)
    test_get_all_todos(token)
    test_get_sorted_todos()
    test_get_todos_by_category()
