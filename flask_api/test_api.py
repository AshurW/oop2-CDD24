import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'

def test_create_todo():
    """Skapa en ny todo med deadline och kategori"""
    deadline = (datetime.now() + timedelta(days=7)).isoformat()
    response = requests.post(
        f'{BASE_URL}/todos',
        json={
            'title': 'Lära mig Flask',
            'deadline': deadline,
            'category': 'Studier'
        }
    )
    print("Skapa todo:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}\\n")

def test_get_all_todos():
    """Hämta alla todos"""
    response = requests.get(f'{BASE_URL}/todos')
    print("Hämta alla todos:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}\\n")

def test_get_sorted_todos():
    """Hämta todos sorterade efter deadline"""
    response = requests.get(f'{BASE_URL}/todos/sort/deadline')
    print("Hämta todos sorterade efter deadline:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}\\n")

def test_get_todos_by_category():
    """Hämta todos efter kategori"""
    response = requests.get(f'{BASE_URL}/todos/category/Studier')
    print("Hämta todos efter kategori:")
    print(f"Statuskod: {response.status_code}")
    print(f"Svar: {response.json()}\\n")

if __name__ == '__main__':
    # Testa alla endpoints
    test_create_todo()
    test_get_all_todos()
    test_get_sorted_todos()
    test_get_todos_by_category()
