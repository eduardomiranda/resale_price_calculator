# Resale price calculator


&nbsp;
## Criando o Python Virtual Environment
Necessário apenas um única vez.

```sh
python3  -m  venv  myvenv
```

\
&nbsp;
## Ativando o Virtual Environment
**Necessário toda vez** que for executar o código.

```sh
source  myvenv/bin/activate
```

# Install dependencies
```sh
pip install -r requirements.txt
```

# Run the application
```sh
streamlit run main.py
```

# Run tests
```sh
pytest
```

# Format code
```sh
black .
isort .
```

# Type checking
```sh
mypy .
```


# Current Project Structure:
resale_price_calculator/
├── main.py                 # Application entry point
├── constants.py            # Centralized constants
├── requirements.txt        # Dependencies
├── pyproject.toml         # Project configuration
├── .pre-commit-config.yaml # Code quality hooks
├── domain/
│   ├── __init__.py
│   └── pricing.py         # Business logic
├── ui/
│   ├── __init__.py
│   └── components.py      # UI components
└── tests/
    ├── __init__.py
    └── test_pricing.py    # Comprehensive tests