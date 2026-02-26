# Лабы по предмету "Тестирование программного обеспечения"

## Запуск

Установка зависимостей:

```powershell
python -m pip install -r requirements.txt
```

Запуск тестов:

```powershell
python -m pytest -q
```

Покрытие:

```powershell
coverage run --rcfile=.coveragerc -m pytest -q
coverage report -m
```
