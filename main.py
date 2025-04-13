from utils import ensure_dictionaries, ensure_directory_exists, dictionaries
from data_generation import generate_combined_example
from dataset_utils import generate_and_save_dataset

if __name__ == "__main__":
    ensure_dictionaries()
    ensure_directory_exists('data')

    words, labels = generate_combined_example(dictionaries)  # Передаем dictionaries как параметр
    print("Пример сгенерированных данных:")
    for word, label in zip(words, labels):
        print(word, label)

    generate_and_save_dataset(100, "data/small_dataset.conll")
