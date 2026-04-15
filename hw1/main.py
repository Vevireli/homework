# В рамках этого практического задания вам нужно
# будет создавать веб-сервисы, предоставляющие доступ
# к своей функциональности через REST API.
# Задание 1
# Создайте веб-сервис, который генерирует предсказание (аналог печенья с предсказаниями)
# Задание 2
# Создайте веб-сервис, которые будет генерировать случайные числа.Требуется создать такую функциональность:
# ■ Генерация случайного числа;
# ■ Генерация случайного числа в диапазоне;
# ■ Генерация набора случайных чисел.
# Задание 3
# Создайте веб-сервис, который будет возвращать текст
# стиха. Требуется создать следующую функциональность:
# ■ Случайный стих;
# ■ Случайный стих автора;
# ■ Случайный стих по тематике (любовь, творчество,
# жизнь и т. д.).
# Задание 4
# К сервису из третьего задания нужно добавить функциональность:
# ■ Названия всех стихов автора;
# ■ Список всех авторов;
# ■ Список всех тематик;
# ■ Названия всех стихов по указанной тематике.

import json
import random
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional

app = FastAPI(title="Fortune & Random & Poetry Service")

# ---------- Загрузка стихов ----------
with open("poems_data.json", "r", encoding="utf-8") as f:
    poems = json.load(f)

# ---------- Предсказания для задания 1 ----------
FORTUNES = [
    "Сегодня вас ждёт приятный сюрприз.",
    "Удача будет на вашей стороне.",
    "Не бойтесь перемен – они к лучшему.",
    "Вам предстоит интересное знакомство.",
    "Берегите здоровье, оно важнее всего.",
    "Ваша смелость приведёт к успеху."
]

# ========== Задание 1: генерация предсказания ==========
@app.get("/fortune", summary="Случайное предсказание")
async def get_fortune():
    return {"fortune": random.choice(FORTUNES)}

# ========== Задание 2: случайные числа ==========
@app.get("/random", summary="Случайное число от 0 до 1")
async def random_float():
    return {"value": random.random()}

@app.get("/random/range", summary="Случайное число в заданном диапазоне")
async def random_in_range(min: float = Query(0, description="Нижняя граница"),
                          max: float = Query(1, description="Верхняя граница")):
    if min >= max:
        raise HTTPException(400, "min должно быть меньше max")
    return {"value": random.uniform(min, max)}

@app.post("/random/multi", summary="Набор случайных чисел")
async def random_multiple(count: int = Query(1, ge=1, le=100, description="Количество чисел"),
                          min: float = Query(0), max: float = Query(1)):
    if min >= max:
        raise HTTPException(400, "min должно быть меньше max")
    numbers = [random.uniform(min, max) for _ in range(count)]
    return {"numbers": numbers}

# ========== Задание 3: стихи ==========
@app.get("/poem/random", summary="Случайный стих")
async def random_poem():
    return random.choice(poems)

@app.get("/poem/random/author", summary="Случайный стих указанного автора")
async def random_poem_by_author(author: str = Query(..., description="Имя автора")):
    filtered = [p for p in poems if p["author"].lower() == author.lower()]
    if not filtered:
        raise HTTPException(404, f"Автор '{author}' не найден")
    return random.choice(filtered)

@app.get("/poem/random/topic", summary="Случайный стих по тематике")
async def random_poem_by_topic(topic: str = Query(..., description="Тема (любовь, жизнь, творчество...)")):
    filtered = [p for p in poems if p["topic"].lower() == topic.lower()]
    if not filtered:
        raise HTTPException(404, f"Тема '{topic}' не найдена")
    return random.choice(filtered)

# ========== Задание 4: дополнительная информация ==========
@app.get("/poem/titles/author", summary="Все названия стихов автора")
async def titles_by_author(author: str = Query(...)):
    titles = [p["title"] for p in poems if p["author"].lower() == author.lower()]
    if not titles:
        raise HTTPException(404, f"Автор '{author}' не найден")
    return {"author": author, "titles": titles}

@app.get("/authors", summary="Список всех авторов")
async def list_authors():
    authors = sorted(set(p["author"] for p in poems))
    return {"authors": authors}

@app.get("/topics", summary="Список всех тематик")
async def list_topics():
    topics = sorted(set(p["topic"] for p in poems))
    return {"topics": topics}

@app.get("/poem/titles/topic", summary="Названия всех стихов по тематике")
async def titles_by_topic(topic: str = Query(...)):
    titles = [p["title"] for p in poems if p["topic"].lower() == topic.lower()]
    if not titles:
        raise HTTPException(404, f"Тема '{topic}' не найдена")
    return {"topic": topic, "titles": titles}