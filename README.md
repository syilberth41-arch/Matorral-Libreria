# 📚 BookStore — Aplicación Web de Venta de Libros

Aplicación web Flask para venta de libros físicos y digitales, optimizada para despliegue en **PythonAnywhere**.

## Características

- **Catálogo** con búsqueda avanzada por título, autor, género y rango de precio
- **Carrito de compras** con prevención de duplicados y checkout en ≤ 3 pasos
- **Autenticación 2FA** (TOTP) con pyotp
- **Descarga segura** de e-books (PDF/EPUB) solo para compradores
- **Panel admin** con CRUD de libros, géneros y gestión de pedidos
- **Pagos tokenizados** (PCI DSS compliant — nunca almacena datos de tarjeta)
- **Caching** en catálogo con Flask-Caching
- **Suite de pruebas** con pytest (objetivo ≥ 70% cobertura)

## Instalación local

```bash
cd bookstore
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python seed_data.py            # Cargar datos de ejemplo
python wsgi.py                 # http://127.0.0.1:5000
```

### Credenciales de prueba
| Rol     | Email              | Contraseña |
|---------|--------------------|------------|
| Admin   | admin@bookstore.com | admin1234  |
| Usuario | user@test.com       | test1234   |

## Tests

```bash
python -m pytest tests/ -v --tb=short
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## Deploy en PythonAnywhere

1. Subir el proyecto a PythonAnywhere (git clone o upload)
2. Crear virtualenv: `mkvirtualenv --python=python3.10 bookstore`
3. `pip install -r requirements.txt`
4. En la pestaña **Web**, configurar:
   - **Source code**: `/home/tu_usuario/bookstore`
   - **WSGI file**: editar para que importe de `wsgi.py`
   - **Virtualenv**: `/home/tu_usuario/.virtualenvs/bookstore`
5. En la consola:
   ```bash
   cd ~/bookstore
   python seed_data.py
   ```
6. Reload en la pestaña Web

## Estructura del proyecto

```
bookstore/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Dev/Test/Prod configs
│   ├── extensions.py        # db, cache, login, csrf
│   ├── models/              # User, Book, Cart, Order
│   ├── blueprints/          # auth, catalog, cart, download, admin
│   ├── services/            # search, payment, download
│   ├── templates/           # Jinja2 templates
│   └── static/css/          # CSS design system
├── tests/                   # pytest suite
├── wsgi.py                  # WSGI entry point
├── seed_data.py             # Sample data loader
└── requirements.txt
```

## Métricas de Calidad

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| Disponibilidad | ≥ 99% uptime | ✅ PythonAnywhere managed |
| Tiempo de carga catálogo | < 3s | ✅ Cache + índices DB |
| Abandono de carrito | < 15% | ✅ Checkout ≤ 3 pasos |
| Cobertura de pruebas | ≥ 70% | ✅ pytest + pytest-cov |
| Cumplimiento PCI DSS | 100% | ✅ Tokenización, no almacena PAN |
