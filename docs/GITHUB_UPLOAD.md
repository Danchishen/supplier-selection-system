# Как выложить проект на GitHub

## Вариант 1: через сайт GitHub

1. Зайди на GitHub под своим аккаунтом.
2. Нажми **New repository**.
3. Название репозитория: `supplier-selection-system`.
4. Description: `Flask application for multicriteria supplier selection using AHP, entropy, variance weights and TOPSIS.`
5. Выбери **Public**.
6. Не добавляй README, `.gitignore` и License через сайт, потому что они уже есть в проекте.
7. Нажми **Create repository**.
8. На компьютере открой папку проекта в терминале и выполни команды из раздела ниже.

## Команды для загрузки

```bash
cd supplier-selection-system

git init
git add .
git commit -m "Initial supplier selection Flask app"
git branch -M main
git remote add origin https://github.com/Danchishen/supplier-selection-system.git
git push -u origin main
```

Если GitHub попросит авторизацию, используй вход через браузер или Personal Access Token вместо пароля.

## Проверка перед загрузкой

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

После запуска открой в браузере:

```text
http://127.0.0.1:5000
```

## Что добавить после первой загрузки

1. Скриншоты интерфейса в папку `screenshots/`.
2. Ссылку на репозиторий в резюме.
3. Краткое описание проекта в профиль GitHub или LinkedIn.
4. При желании — деплой на Render, Railway или PythonAnywhere.
