from utils import ensure_dictionaries, dictionaries
from data_generation import generate_combined_example

def save_conll_dataset(dataset, filename="dataset.conll"):
    """
    Сохраняет датасет в формате CoNLL с правильной кодировкой
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for words, labels in dataset:
            for word, label in zip(words, labels):
                try:
                    f.write(f"{word} {label}\n")
                except UnicodeEncodeError:
                    # В случае проблем с кодировкой используем безопасный вариант
                    f.write(f"{word.encode('utf-8').decode('utf-8')} {label}\n")
            f.write("\n")  # Пустая строка между предложениями


def analyze_entity_count(dataset):
    """
    Анализирует количество сущностей каждого типа и причины разрывов
    """
    entity_counts = {}
    split_entities = {}
    entity_examples = {}

    for words, labels in dataset:
        i = 0
        max_iterations = len(labels) * 2  # Ограничение цикла
        iteration_count = 0

        while i < len(labels) and iteration_count < max_iterations:
            iteration_count += 1
            if labels[i].startswith('B-'):
                entity_type = labels[i][2:]
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

                # Проверяем, есть ли следующий токен с I- той же сущности
                j = i + 1
                entity_parts = [words[i]]
                inner_iteration = 0
                max_inner_iterations = len(labels) - j  # Ограничение для внутреннего цикла

                while j < len(labels) and labels[j] == f"I-{entity_type}" and inner_iteration < max_inner_iterations:
                    inner_iteration += 1
                    entity_parts.append(words[j])
                    j += 1

                # Проверяем, есть ли следующий токен с B- той же сущности
                # (возможное разделение из-за знаков препинания)
                if j < len(labels) and j + 1 < len(labels):
                    if labels[j] == "O" and labels[j + 1] == f"B-{entity_type}":
                        # Нашли потенциальное разделение
                        current_entity = " ".join(entity_parts)
                        split_entities[entity_type] = split_entities.get(entity_type, 0) + 1

                        # Сохраняем пример для анализа
                        context_start = max(0, i - 2)
                        context_end = min(len(words), j + 3)
                        context = [(words[k], labels[k]) for k in range(context_start, context_end)]

                        if entity_type not in entity_examples:
                            entity_examples[entity_type] = []

                        if len(entity_examples[entity_type]) < 3:  # Сохраняем до 3 примеров для каждого типа
                            entity_examples[entity_type].append(context)

                i = j
            else:
                i += 1

    return entity_counts, split_entities, entity_examples


def count_real_entities(dataset):
    """
    Подсчитывает реальное количество сущностей в датасете,
    без учета разделения префиксами и знаками пунктуации
    """
    # Сначала подсчитаем количество адресов, имен и т.д. в примерах
    example_entity_counts = {}

    # Для каждого примера считаем, что должна быть 1 сущность каждого типа
    for i, (words, labels) in enumerate(dataset):
        # Проверяем, какие типы сущностей есть в примере
        entity_types = set()
        for label in labels:
            if label.startswith('B-') or label.startswith('I-'):
                entity_type = label[2:]
                entity_types.add(entity_type)

        # Увеличиваем счетчик для каждого типа сущности
        for entity_type in entity_types:
            example_entity_counts[entity_type] = example_entity_counts.get(entity_type, 0) + 1

    return example_entity_counts


def generate_and_save_dataset(num_samples=1000, filename="dataset.conll"):
    """
    Генерирует и сохраняет датасет
    """
    # Проверка и создание словарей
    ensure_dictionaries()

    dataset = []
    # Ограничим количество генерируемых примеров для предотвращения долгого выполнения
    max_examples = min(num_samples, 1000)

    for _ in range(max_examples):
        try:
            words, labels = generate_combined_example(dictionaries)
            dataset.append((words, labels))
        except Exception as e:
            print(f"Ошибка при генерации примера: {e}")
            continue

    save_conll_dataset(dataset, filename)

    # Анализируем количество сущностей и причины разрывов
    entity_counts, split_entities, entity_examples = analyze_entity_count(dataset)

    # Подсчитываем реальное количество сущностей
    real_entity_counts = count_real_entities(dataset)

    print("\nАнализ сущностей в датасете:")
    print(f"Всего сгенерировано примеров: {len(dataset)}")
    print("Количество сущностей по типам:")
    for entity_type in sorted(entity_counts.keys()):
        print(
            f"  {entity_type}: {entity_counts[entity_type]} (размечено как B-) / {real_entity_counts.get(entity_type, 0)} (реальных сущностей)")
        print(f"    Из них разделено префиксами/пунктуацией: {split_entities.get(entity_type, 0)}")

    # Вывод примеров разделенных сущностей для анализа (ограничиваем вывод)
    print("\nПримеры разделенных сущностей (выборочно):")
    count = 0
    for entity_type, examples in entity_examples.items():
        if examples and count < 3:  # Ограничиваем вывод примеров
            print(f"\nТип сущности: {entity_type}")
            for i, context in enumerate(examples[:1]):  # Выводим только первый пример
                print(f"  Пример {i + 1}:")
                for word, label in context:
                    print(f"    {word} {label}")
            count += 1

    return dataset