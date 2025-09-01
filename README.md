# 📚 Book Sharing App

Una aplicación para compartir libros entre amigos, desarrollada con FastAPI y PostgreSQL.

## 🚀 Características

- Sistema de autenticación JWT
- Gestión de bibliotecas personales
- Grupos de amigos para compartir libros
- Sistema de préstamos con chat integrado
- OCR para extraer información de libros desde fotos
- Integración con APIs externas (OpenLibrary, Google Books)

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Autenticación**: JWT con Passlib
- **OCR**: EasyOCR
- **APIs Externas**: OpenLibrary, Google Books
- **Testing**: Pytest

## 📁 Estructura del Proyecto

```
book_sharing_app/
├── app/
│   ├── models/          # Modelos SQLAlchemy
│   ├── schemas/         # Schemas Pydantic
│   ├── api/            # Endpoints FastAPI
│   ├── services/       # Lógica de negocio
│   └── utils/          # Utilidades
├── tests/              # Tests
├── alembic/            # Migraciones
└── uploads/            # Archivos temporales
```

## 🚀 Instalación

1. **Clonar el repositorio**
2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```
3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurar base de datos**
   ```bash
   docker-compose up -d
   ```
5. **Configurar variables de entorno**
   ```bash
   cp env.example .env
   # Editar .env con tus valores
   ```

## 📝 Roadmap

Este proyecto está diseñado para aprendizaje progresivo:

- **Semana 1**: Setup inicial y autenticación
- **Semana 2**: Gestión de libros y APIs externas
- **Semana 3**: Sistema de grupos
- **Semana 4**: Sistema de préstamos
- **Semana 5**: Chat y comunicación
- **Semana 6**: Testing y deployment

## 📚 Recursos de Aprendizaje

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [OpenLibrary API](https://openlibrary.org/developers/api)

---

**¡Disfruta aprendiendo! 🎓**
