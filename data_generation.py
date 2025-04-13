# data_generation.py

import random
from faker import Faker
import json

fake = Faker('ru_RU')

# Загружаем шаблоны из JSON файла
def load_templates(file_path='templates.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Загружаем шаблоны для комбинированных примеров
templates = load_templates()

address_templates = templates["address_templates"]
name_templates = templates["name_templates"]
phone_templates = templates["phone_templates"]
email_templates = templates["email_templates"]
combined_example_templates = templates["combined_example_templates"]

def generate_address(dictionaries):
    template = random.choice(address_templates)
    address = template
    for entity_type, values in dictionaries.items():
        if f"{{{entity_type}}}" in address:
            address = address.replace(f"{{{entity_type}}}", random.choice(values))
    entity_map = {entity_type: [value for value in values if value in address] for entity_type, values in dictionaries.items()}
    return address, entity_map

def generate_person():
    first_name = fake.first_name()
    last_name = fake.last_name()
    middle_name = fake.middle_name()
    template = random.choice(name_templates)
    name = template.replace("{ИМЯ}", first_name).replace("{ФАМИЛИЯ}", last_name).replace("{ОТЧЕСТВО}", middle_name)
    entity_map = {"ИМЯ": [first_name],
                  "ФАМИЛИЯ": [last_name],
                  "ОТЧЕСТВО": [middle_name]}

    return name, entity_map

def generate_phone():
    return random.choice(phone_templates)

def generate_email():
    first_name = fake.first_name()
    last_name = fake.last_name()
    return random.choice(email_templates).format(first_name=first_name, last_name=last_name)

def generate_combined_example(dictionaries):
    from tokenization import find_entity_tokens
    from annotation import create_bio_annotations

    # Генерация данных для имени и адреса
    name, name_entity_map = generate_person()
    address, address_entity_map = generate_address(dictionaries)

    # Генерация данных для телефона и email
    phone = generate_phone()
    email = generate_email()

    # Обновляем entity_map с новыми сущностями
    entity_map = {**name_entity_map, **address_entity_map}
    entity_map["PHONE"] = [phone]
    entity_map["EMAIL"] = [email]

    # Выбираем случайный шаблон и формируем текст
    text = random.choice(combined_example_templates).format(name=name, address=address, phone=phone, email=email)

    # Находим сущности в тексте
    entity_tokens = find_entity_tokens(text, entity_map, dictionaries)

    # Создаём BIO-разметку
    words, labels = create_bio_annotations(text, entity_tokens, dictionaries)

    return words, labels
