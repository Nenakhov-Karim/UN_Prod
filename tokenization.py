def expand_entity_map_with_prefixes(entity_map, text):
    stop_words = {"по", "в", "на", "за", "из", "у", "к", "с", "от", "до", "для", "про", "через", "а", "и", "но", "или",
                  "что", "как", "при"}
    prefixes = {
        "ГОРОД": ["г.", "с.", "д.", "п.", "ст.", "клх.", "к."],
        "УЛИЦА": ["ул.", "пер.", "пр.", "бул.", "алл.", "наб.", "ш."]
    }

    expanded = entity_map.copy()
    for entity_type, entity_list in entity_map.items():
        clean_list = [e for e in entity_list if isinstance(e, str) and e.strip() and e.lower() not in stop_words]
        if entity_type in ["ИМЯ", "ФАМИЛИЯ", "ОТЧЕСТВО"]:
            expanded[entity_type] = clean_list
        elif entity_type in prefixes:
            prefixed = []
            for entity in clean_list:
                for prefix in prefixes[entity_type]:
                    prefixed.append(f"{prefix} {entity}")
                    prefixed.append(f"{prefix}{entity}")
            expanded[entity_type] = clean_list + prefixed
        else:
            expanded[entity_type] = clean_list
    return expanded


def find_sentence_start_entities(text, entity_map):
    stop_words = {"по", "в", "на", "за", "из", "у", "к", "с", "от", "до", "для", "про", "через", "а", "и", "но", "или",
                  "что", "как", "при"}
    tokens = []

    sentence_starts = [0]
    for i in range(1, len(text)):
        if text[i - 1] in ".!?" and i < len(text) - 1 and text[i].isspace() and text[i + 1].isupper():
            sentence_starts.append(i + 1)

    for start_pos in sentence_starts:
        end_pos = start_pos
        while end_pos < len(text) and not text[end_pos].isspace():
            end_pos += 1
        word = text[start_pos:end_pos].strip()
        if word and word[0].isupper() and word.lower() not in stop_words:
            for t in ["ИМЯ", "ФАМИЛИЯ"]:
                for val in entity_map.get(t, []):
                    if val.lower() == word.lower():
                        tokens.append((word, t, start_pos))
    return tokens


def find_line_start_entities(text, entity_map):
    stop_words = {"по", "в", "на", "за", "из", "у", "к", "с", "от", "до", "для", "про", "через", "а", "и", "но", "или",
                  "что", "как", "при"}
    tokens = []
    lines = text.split('\n')
    pos = 0
    for line in lines:
        line = line.strip()
        if line:
            first_word = line.split()[0]
            if first_word[0].isupper() and first_word.lower() not in stop_words:
                for t in ["ИМЯ", "ФАМИЛИЯ"]:
                    for val in entity_map.get(t, []):
                        if val.lower() == first_word.lower():
                            tokens.append((first_word, t, pos))
        pos += len(line) + 1
    return tokens


def search_entities_in_text(normalized_text, expanded_entity_map, original_entity_map, original_text):
    max_iterations = 1000
    tokens = []

    for entity_type, entity_list in expanded_entity_map.items():
        for entity in entity_list:
            if not entity.strip():
                continue

            entity_lower = entity.lower()
            text_lower = normalized_text.lower()
            start_idx = 0
            iterations = 0

            while iterations < max_iterations:
                iterations += 1
                pos = text_lower.find(entity_lower, start_idx)
                if pos == -1:
                    break
                is_start = pos == 0 or not text_lower[pos - 1].isalnum()
                is_end = pos + len(entity_lower) == len(text_lower) or not text_lower[pos + len(entity_lower)].isalnum()

                if is_start and is_end:
                    tokens.append((original_text[pos:pos + len(entity)], entity_type, pos))

                start_idx = pos + 1
    return tokens


def filter_overlapping_tokens(tokens):
    tokens.sort(key=lambda x: x[2])
    filtered = []
    i = 0
    while i < len(tokens):
        current = tokens[i]
        end = current[2] + len(current[0])
        longest = current
        for j in range(i + 1, len(tokens)):
            if tokens[j][2] < end:
                if tokens[j][2] + len(tokens[j][0]) > end:
                    longest = tokens[j]
                    end = tokens[j][2] + len(tokens[j][0])
            else:
                break
        filtered.append(longest)
        while i < len(tokens) and tokens[i][2] < end:
            i += 1
    return filtered


def find_phone_and_email_tokens(text, entity_map, dictionaries):
    """
    Ищет телефонные номера и email в тексте.
    Добавляет их в список найденных сущностей.
    """
    tokens = []
    # Для телефонов
    for entity in entity_map.get("PHONE", []):
        if entity.lower() in text.lower():
            start_idx = text.lower().find(entity.lower())
            tokens.append((entity, "PHONE", start_idx))

    # Для email
    for entity in entity_map.get("EMAIL", []):
        if entity.lower() in text.lower():
            start_idx = text.lower().find(entity.lower())
            tokens.append((entity, "EMAIL", start_idx))

    return tokens



# Основная функция find_entity_tokens теперь вызывает эти маленькие функции
def find_entity_tokens(text, entity_map, dictionaries):
    normalized_text = text
    expanded_entity_map = expand_entity_map_with_prefixes(entity_map, text)

    tokens = []
    tokens += find_sentence_start_entities(text, entity_map)  # обработка начала предложений
    tokens += find_line_start_entities(text, entity_map)  # обработка начала строк
    tokens += search_entities_in_text(normalized_text, expanded_entity_map, entity_map, text)  # основной поиск

    tokens += find_phone_and_email_tokens(text, entity_map, dictionaries)

    tokens = filter_overlapping_tokens(tokens)  # фильтрация пересечений сущностей
    return tokens
