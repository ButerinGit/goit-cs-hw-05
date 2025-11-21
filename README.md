# goit-cs-hw-05 — Асинхронна обробка + MapReduce

Домашнє завдання з двох частин:
1) **Асинхронне сортування файлів за розширенням**  
2) **MapReduce-аналіз частоти слів + візуалізація**

## Вимоги
- Python 3.9+ (рекомендовано 3.10/3.11)
- Залежності з `requirements.txt`

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## Завдання 1: Асинхронний сортер

**Файл:** `task1_async_sort/sorter_async.py`  
**Що робить:** рекурсивно читає вихідну папку і копіює файли в підпапки директорії призначення за їхнім розширенням. Копіювання виконується паралельно (thread pool) з контролем concurrency.

### Запуск
```bash
python3 task1_async_sort/sorter_async.py   -s ./source   -o ./output   -c 20
```

- `-s/--source` — вихідна папка з файлами
- `-o/--output` — папка призначення (якщо нема — буде створена)
- `-c/--concurrency` — скільки файлів копіювати одночасно (за замовчуванням 10)

### Очікуваний результат
```
output/
├── txt/
├── csv/
├── jpg/
└── no_ext/
```
Усі помилки логуються, збережені метадані файлів (`shutil.copy2`).

---

## Завдання 2: MapReduce + Візуалізація

**Файл:** `task2_mapreduce/mapreduce_wordfreq.py`  
**Що робить:** завантажує текст з URL, ділить на частини, рахує частоти слів у потоках (Map), агрегує (Reduce) і показує графік топ-N слів.

### Запуск (приклад з Gutenberg)
```bash
python3 task2_mapreduce/mapreduce_wordfreq.py   -u "https://www.gutenberg.org/cache/epub/1342/pg1342.txt"   -w 8   -t 20
```

- `-u/--url` — адреса з текстом
- `-w/--workers` — кількість потоків для Map-кроку
- `-t/--top` — скільки слів показати на графіку

> Якщо вікно графіка не з’являється, заміни у функції `visualize_top_words` `plt.show()` на
> `plt.savefig("top_words.png", dpi=200, bbox_inches="tight")` і відкрий файл.

---

## Структура репозиторію
```
goit-cs-hw-05/
├── task1_async_sort/
│   └── sorter_async.py
├── task2_mapreduce/
│   └── mapreduce_wordfreq.py
├── source/           # вихідні файли (для перевірки завдання 1)
├── output/           # результат сортування
├── requirements.txt
└── README.md
```

---

## Чек-ліст перед здачею
- [ ] `sorter_async.py` приймає аргументи CLI, логує помилки, розкладає за розширеннями, працює асинхронно (to_thread + семафор).
- [ ] `mapreduce_wordfreq.py` завантажує текст по URL, виконує MapReduce у потоках, будує графік топ-N.
- [ ] `requirements.txt` встановлюється без помилок.
- [ ] Додано скрін або PNG з графіком (необов’язково, але бажано для наочності).
- [ ] Репозиторій публічний. Архів для LMS названо `ДЗ5_ПІБ.zip`.

---

## Корисні команди
```bash
# відкрити папку у Finder (macOS)
open .

# швидко накидати тест-файли для сортування
echo "hello" > ./source/a.txt
echo "1,2,3" > ./source/b.csv

# локальний текст для MapReduce (без інтернету)
echo "Data science is fun. Data is powerful!" > sample.txt
python3 -m http.server 8000
python3 task2_mapreduce/mapreduce_wordfreq.py -u "http://localhost:8000/sample.txt" -w 4 -t 10
```
