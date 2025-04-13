import os
import random
from faker import Faker
from data_generation import generate_phone, generate_email


fake = Faker('ru_RU')


def load_dictionary(entity_type, default_generator=None, num_fallback=50):
    file_path = f'dictionaries/{entity_type.lower()}.txt'

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            values = [line.strip() for line in f if line.strip()]
        if values:
            return values

    if default_generator:
        return [default_generator() for _ in range(num_fallback)]
    return []


dictionaries = {
    "СТРАНА": load_dictionary("страна", fake.country, 20),
    "РЕГИОН": load_dictionary("регион", fake.region, 30),
    "ГОРОД": load_dictionary("город", fake.city, 50),
    "РАЙОН": load_dictionary("район", lambda: f"район {fake.word().capitalize()}", 30),
    "УЛИЦА": load_dictionary("улица", fake.street_name, 100),
    "ЧИСЛО": load_dictionary("число", lambda: str(random.randint(1, 200)), 100),
    "PHONE": load_dictionary("телефон", generate_phone, 50),
    "EMAIL": load_dictionary("email", generate_email, 50)
}




def ensure_dictionaries():
    if not os.path.exists('dictionaries'):
        os.makedirs('dictionaries')

    for key, values in dictionaries.items():
        file_path = f'dictionaries/{key.lower()}.txt'
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(values))


def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)