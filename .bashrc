# Type check
alias tc="mypy ."

# Format code
alias fmt="black . && isort ."

# Django + Type check
alias check="python manage.py check && mypy ."

# Run server com check antes
alias runserver="mypy . && python manage.py runserver"