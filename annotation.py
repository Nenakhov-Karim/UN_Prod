def post_process_bio_tags(words, labels):
    """
    Пост-обработка BIO-тегов для обеспечения корректной последовательности:
    - Метки I- должны всегда следовать за B- или I- того же типа
    - Если метка I- идет после O, меняем I- на B-
    """
    for i in range(1, len(labels)):
        if labels[i].startswith("I-"):
            entity_type = labels[i][2:]
            # Проверяем, есть ли перед этой I-меткой соответствующая B-/I-метка
            prev_label = labels[i - 1]

            # Если предыдущая метка не является B- или I- того же типа,
            # меняем текущую метку I- на B-
            if prev_label != f"B-{entity_type}" and prev_label != f"I-{entity_type}":
                labels[i] = f"B-{entity_type}"

    return words, labels


def tokenize_text_with_positions(text):
    words = []
    positions = []
    i = 0
    max_iterations = len(text) * 2
    iteration_count = 0

    while i < len(text) and iteration_count < max_iterations:
        iteration_count += 1
        start_i = i

        if text[i].isspace():
            i += 1
            continue

        if text[i] in ",.!?:;()[]{}«»" and (i == 0 or i == len(text) - 1 or text[i-1].isspace() or text[i+1].isspace()):
            words.append(text[i])
            positions.append(i)
        elif text[i] == "-" and i > 0 and i < len(text) - 1 and not text[i-1].isspace() and not text[i+1].isspace():
            start = i
            while i < len(text) and not text[i].isspace() and text[i] not in ",.!?:;()[]{}«»":
                i += 1
            words.append(text[start:i])
            positions.append(start)
        else:
            start = i
            while i < len(text) and not text[i].isspace() and text[i] not in ",.!?:;()[]{}«»-":
                i += 1
            words.append(text[start:i])
            positions.append(start)

        if i == start_i:
            i += 1

    return words, positions


def assign_bio_labels(words, positions, entity_tokens):
    labels = ["O"] * len(words)

    for entity, entity_type, start_pos in entity_tokens:
        entity_end = start_pos + len(entity)
        entity_word_indices = []

        for i, pos in enumerate(positions):
            if (pos >= start_pos and pos < entity_end) or (pos < start_pos and positions[i] + len(words[i]) > start_pos):
                entity_word_indices.append(i)

        if entity_word_indices:
            labels[entity_word_indices[0]] = f"B-{entity_type}"
            for idx in entity_word_indices[1:]:
                labels[idx] = f"I-{entity_type}"

    return labels


def handle_prefixes(words, positions, labels):
    prefix_entity_types = {
        "г": "ГОРОД", "с": "ГОРОД", "д": "ГОРОД", "п": "ГОРОД", "ст": "ГОРОД", "клх": "ГОРОД", "к": "ГОРОД",
        "ул": "УЛИЦА", "пер": "УЛИЦА", "пр": "УЛИЦА", "бул": "УЛИЦА", "алл": "УЛИЦА", "наб": "УЛИЦА", "ш": "УЛИЦА"
    }

    for i in range(len(words) - 1):
        if words[i].lower() in prefix_entity_types:
            entity_type = prefix_entity_types[words[i].lower()]
            if entity_type in ["ГОРОД", "УЛИЦА"]:
                labels[i] = f"B-{entity_type}"
                labels[i + 1] = f"I-{entity_type}"

    return labels


def fix_bio_errors(words, labels):
    for i in range(1, len(labels)):
        if labels[i].startswith("I-"):
            entity_type = labels[i][2:]
            prev_label = labels[i - 1]
            if prev_label != f"B-{entity_type}" and prev_label != f"I-{entity_type}":
                labels[i] = f"B-{entity_type}"
    return words, labels



def add_phone_and_email_labels(words, labels, dictionaries):
    """
    Добавляет метки для телефонов и email в тексте на основе данных из словаря.
    """
    for i, word in enumerate(words):
        # Проверка на наличие телефона
        if word.lower() in dictionaries["PHONE"]:
            labels[i] = f"B-PHONE"

        # Проверка на наличие email
        elif word.lower() in dictionaries["EMAIL"]:
            labels[i] = f"B-EMAIL"

    return labels




def create_bio_annotations(text, entity_tokens, dictionaries):
    words, positions = tokenize_text_with_positions(text)
    labels = assign_bio_labels(words, positions, entity_tokens)
    labels = add_phone_and_email_labels(words, labels, dictionaries)
    labels = handle_prefixes(words, positions, labels)
    words, labels = fix_bio_errors(words, labels)
    return words, labels

def post_process_bio_tags(words, labels):
    """
    Пост-обработка BIO-тегов для обеспечения корректной последовательности:
    - Метки I- должны всегда следовать за B- или I- того же типа
    - Если метка I- идет после O, меняем I- на B-
    """
    for i in range(1, len(labels)):
        if labels[i].startswith("I-"):
            entity_type = labels[i][2:]
            # Проверяем, есть ли перед этой I-меткой соответствующая B-/I-метка
            prev_label = labels[i - 1]

            # Если предыдущая метка не является B- или I- того же типа,
            # меняем текущую метку I- на B-
            if prev_label != f"B-{entity_type}" and prev_label != f"I-{entity_type}":
                labels[i] = f"B-{entity_type}"

    return words, labels


def tokenize_text_with_positions(text):
    words = []
    positions = []
    i = 0
    max_iterations = len(text) * 2
    iteration_count = 0

    while i < len(text) and iteration_count < max_iterations:
        iteration_count += 1
        start_i = i

        if text[i].isspace():
            i += 1
            continue

        if text[i] in ",.!?:;()[]{}«»" and (i == 0 or i == len(text) - 1 or text[i-1].isspace() or text[i+1].isspace()):
            words.append(text[i])
            positions.append(i)
        elif text[i] == "-" and i > 0 and i < len(text) - 1 and not text[i-1].isspace() and not text[i+1].isspace():
            start = i
            while i < len(text) and not text[i].isspace() and text[i] not in ",.!?:;()[]{}«»":
                i += 1
            words.append(text[start:i])
            positions.append(start)
        else:
            start = i
            while i < len(text) and not text[i].isspace() and text[i] not in ",.!?:;()[]{}«»-":
                i += 1
            words.append(text[start:i])
            positions.append(start)

        if i == start_i:
            i += 1

    return words, positions


def assign_bio_labels(words, positions, entity_tokens):
    labels = ["O"] * len(words)

    for entity, entity_type, start_pos in entity_tokens:
        entity_end = start_pos + len(entity)
        entity_word_indices = []

        for i, pos in enumerate(positions):
            if (pos >= start_pos and pos < entity_end) or (pos < start_pos and positions[i] + len(words[i]) > start_pos):
                entity_word_indices.append(i)

        if entity_word_indices:
            labels[entity_word_indices[0]] = f"B-{entity_type}"
            for idx in entity_word_indices[1:]:
                labels[idx] = f"I-{entity_type}"

    return labels


def handle_prefixes(words, positions, labels):
    prefix_entity_types = {
        "г": "ГОРОД", "с": "ГОРОД", "д": "ГОРОД", "п": "ГОРОД", "ст": "ГОРОД", "клх": "ГОРОД", "к": "ГОРОД",
        "ул": "УЛИЦА", "пер": "УЛИЦА", "пр": "УЛИЦА", "бул": "УЛИЦА", "алл": "УЛИЦА", "наб": "УЛИЦА", "ш": "УЛИЦА"
    }

    for i in range(len(words) - 1):
        if words[i].lower() in prefix_entity_types:
            entity_type = prefix_entity_types[words[i].lower()]
            if entity_type in ["ГОРОД", "УЛИЦА"]:
                labels[i] = f"B-{entity_type}"
                labels[i + 1] = f"I-{entity_type}"

    return labels


def fix_bio_errors(words, labels):
    for i in range(1, len(labels)):
        if labels[i].startswith("I-"):
            entity_type = labels[i][2:]
            prev_label = labels[i - 1]
            if prev_label != f"B-{entity_type}" and prev_label != f"I-{entity_type}":
                labels[i] = f"B-{entity_type}"
    return words, labels



def add_phone_and_email_labels(words, labels, dictionaries):
    """
    Добавляет метки для телефонов и email в тексте на основе данных из словаря.
    """
    for i, word in enumerate(words):
        # Проверка на наличие телефона
        if word.lower() in dictionaries["PHONE"]:
            labels[i] = f"B-PHONE"

        # Проверка на наличие email
        elif word.lower() in dictionaries["EMAIL"]:
            labels[i] = f"B-EMAIL"

    return labels




def create_bio_annotations(text, entity_tokens, dictionaries):
    words, positions = tokenize_text_with_positions(text)
    labels = assign_bio_labels(words, positions, entity_tokens)
    labels = add_phone_and_email_labels(words, labels, dictionaries)
    labels = handle_prefixes(words, positions, labels)
    words, labels = fix_bio_errors(words, labels)
    return words, labels

