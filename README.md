# Fijazo API

API para gestionar apuestas deportivas y llevar un registro personal del historial de apuestas
de cada usuario. MVP centrado en **autenticación de usuarios** y **gestión de apuestas**.

## Tecnologías

- **FastAPI** + **Pydantic v2**
- **MongoDB** (driver async oficial de PyMongo, `AsyncMongoClient`)
- **JWT** (PyJWT) + **bcrypt** para hashing de contraseñas
- **Clean Architecture** + **Repository Pattern**
- **Docker** / **Docker Compose**
- Configuración por variables de entorno (`.env`)

## Arquitectura

```
src/fijazo_api/
├── core/            # config, seguridad (JWT/bcrypt), excepciones de dominio
├── domain/          # entidades e interfaces de repositorio (sin dependencias externas)
│   ├── entities/
│   └── repositories/
├── application/     # casos de uso / servicios (reglas de negocio)
│   └── services/
├── infrastructure/  # implementación MongoDB de los repositorios, conexión, seed
│   ├── database/
│   └── repositories/
├── api/             # capa web: routers, schemas Pydantic, dependencias (DI)
│   ├── routers/
│   └── schemas/
└── main.py          # app factory, lifespan, manejo global de excepciones
```

Las dependencias apuntan siempre hacia el dominio. Para añadir en el futuro **estadísticas,
rankings o análisis de rendimiento** basta con crear nuevos casos de uso y, si hace falta, nuevos
repositorios, sin modificar el núcleo (dominio) ni la infraestructura base.

## Puesta en marcha con Docker Compose (recomendado)

```bash
cp .env.example .env      # ajusta JWT_SECRET y credenciales de admin
docker compose up --build
```

- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- MongoDB expuesto en `localhost:27017`

Al arrancar se crean los índices únicos y se siembra el usuario **ADMIN** definido en `.env`.

## Ejecución local (sin Docker)

Requiere Python 3.14+, Poetry y una instancia de MongoDB en `localhost:27017`.

```bash
poetry install
cp .env.example .env
poetry run uvicorn fijazo_api.main:app --reload
```

## Endpoints

### Autenticación
| Método | Ruta             | Descripción                          |
|--------|------------------|--------------------------------------|
| POST   | `/auth/register` | Registro de usuario                  |
| POST   | `/auth/login`    | Login, devuelve un token JWT         |
| GET    | `/users/me`      | Perfil del usuario autenticado       |

### Apuestas (requieren `Authorization: Bearer <token>`)
| Método | Ruta          | Descripción                                        |
|--------|---------------|----------------------------------------------------|
| POST   | `/bets`       | Crear una apuesta                                  |
| GET    | `/bets`       | Listar apuestas propias (paginación + filtros)     |
| GET    | `/bets/{id}`  | Consultar una apuesta por ID                       |
| PUT    | `/bets/{id}`  | Editar una apuesta                                 |
| DELETE | `/bets/{id}`  | Eliminar una apuesta                               |

Filtros de `GET /bets`: `page`, `page_size`, `status`, `sport`, `bet_type`.

### Campos calculados de una apuesta
- `potential_return = stake × odds`
- `potential_profit = stake × (odds − 1)`
- `implied_probability = 1 / odds`
- `created_at`, `updated_at`

## Reglas de validación

- Usuario: 3–15 caracteres · Contraseña: 8–64 caracteres.
- Email y username únicos (validado en servicio + índice único en MongoDB).
- Cuota (`odds`) > 1 · Stake > 0 · Campos obligatorios no vacíos.
- Cada apuesta pertenece únicamente al usuario autenticado.

## Tests

Los tests de integración requieren una instancia de MongoDB accesible (por defecto
`mongodb://localhost:27017`, configurable con `TEST_MONGO_URI`). Usan una base de datos separada
(`fijazo_test`) que se limpia entre pruebas.

```bash
# Con el mongo de docker-compose levantado, o un mongo local:
poetry run pytest
```
