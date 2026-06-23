from __future__ import annotations

from .models import ExternalSkill, StackDefinition


REGISTRY = {
    "flutter": StackDefinition(
        id="flutter",
        name="Flutter / Dart",
        commands={
            "Install dependencies": "flutter pub get",
            "Analyze": "flutter analyze",
            "Test": "flutter test",
            "Run": "flutter run",
            "Build Android APK": "flutter build apk",
        },
        directories=["lib/", "test/", "android/", "ios/", "web/"],
        avoid=["build/", ".dart_tool/", ".flutter-plugins", ".flutter-plugins-dependencies"],
        rules=[
            "Follow Flutter and Dart conventions.",
            "Keep widgets small, readable, and composable.",
            "Prefer StatelessWidget when local mutable state is not needed.",
            "Run flutter analyze and flutter test before finalizing changes when possible.",
            "Do not edit generated build artifacts.",
        ],
        external_skills=[
            ExternalSkill(
                id="flutter-official",
                name="Flutter official agent skills",
                url="https://github.com/flutter/skills",
                install_path=".ai/skills/flutter",
                trusted=True,
            )
        ],
    ),
    "react": StackDefinition(
        id="react",
        name="React / Node",
        commands={
            "Install dependencies": "npm install",
            "Dev server": "npm run dev",
            "Build": "npm run build",
            "Test": "npm test",
        },
        directories=["src/", "public/", "components/", "pages/", "app/"],
        avoid=["node_modules/", "dist/", "build/", ".next/", ".vite/"],
        rules=[
            "Follow the package manager already used by the project.",
            "Keep components focused and reusable.",
            "Prefer TypeScript when the project already uses it.",
            "Do not edit generated build output.",
            "Run lint, tests, or build scripts when available.",
        ],
    ),
    "laravel": StackDefinition(
        id="laravel",
        name="Laravel / PHP",
        commands={
            "Install dependencies": "composer install",
            "Run server": "php artisan serve",
            "Test": "php artisan test",
            "Migrate": "php artisan migrate",
        },
        directories=["app/", "routes/", "database/migrations/", "resources/", "tests/"],
        avoid=["vendor/", "storage/logs/", ".env"],
        rules=[
            "Follow Laravel conventions and existing project structure.",
            "Use artisan commands where appropriate.",
            "Do not edit .env directly unless explicitly requested.",
            "Place migrations in database/migrations.",
            "Add or update tests for behavior changes when practical.",
        ],
    ),
    "python": StackDefinition(
        id="python",
        name="Python",
        commands={
            "Create virtual environment": "python -m venv .venv",
            "Install dependencies": "pip install -r requirements.txt",
            "Test": "pytest",
        },
        directories=["src/", "tests/", "app/"],
        avoid=[".venv/", "__pycache__/", ".pytest_cache/", "dist/", "build/"],
        rules=[
            "Follow the existing Python style and project layout.",
            "Prefer small, typed, testable functions.",
            "Do not commit virtual environments or cache directories.",
            "Use the dependency system already present in the project.",
            "Run tests when available before finalizing changes.",
        ],
    ),
    "fastapi": StackDefinition(
        id="fastapi",
        name="FastAPI",
        commands={
            "Install dependencies": "pip install -r requirements.txt",
            "Run API": "uvicorn main:app --reload",
            "Test": "pytest",
        },
        directories=["app/", "routers/", "tests/"],
        avoid=[".venv/", "__pycache__/", ".pytest_cache/"],
        rules=[
            "Use FastAPI routers and dependency injection where appropriate.",
            "Keep request and response schemas explicit.",
            "Avoid blocking operations inside async endpoints.",
            "Add tests for API behavior when practical.",
        ],
    ),
    "django": StackDefinition(
        id="django",
        name="Django",
        commands={
            "Install dependencies": "pip install -r requirements.txt",
            "Run server": "python manage.py runserver",
            "Migrate": "python manage.py migrate",
            "Test": "python manage.py test",
        },
        directories=["apps/", "templates/", "static/", "tests/"],
        avoid=[".venv/", "__pycache__/", "db.sqlite3"],
        rules=[
            "Follow Django conventions and existing app structure.",
            "Keep models, views, serializers, and urls organized by app.",
            "Create migrations for model changes.",
            "Run Django tests when available.",
        ],
    ),
    "go": StackDefinition(
        id="go",
        name="Go",
        commands={
            "Download dependencies": "go mod download",
            "Run tests": "go test ./...",
            "Build": "go build ./...",
            "Format": "gofmt -w .",
        },
        directories=["cmd/", "internal/", "pkg/"],
        avoid=["bin/", "dist/", "vendor/"],
        rules=[
            "Follow idiomatic Go conventions.",
            "Keep packages small and cohesive.",
            "Run gofmt on changed Go files.",
            "Run go test ./... when practical.",
        ],
    ),
    "docker": StackDefinition(
        id="docker",
        name="Docker",
        commands={
            "Build image": "docker build .",
            "Compose up": "docker compose up -d",
            "Compose logs": "docker compose logs -f",
        },
        directories=[],
        avoid=["volumes/", ".docker/"],
        rules=[
            "Keep Dockerfiles minimal and reproducible.",
            "Do not hardcode secrets into Dockerfiles or compose files.",
            "Prefer .dockerignore to reduce build context size.",
            "Document required environment variables.",
        ],
    ),
    "github-actions": StackDefinition(
        id="github-actions",
        name="GitHub Actions",
        commands={},
        directories=[".github/workflows/"],
        avoid=[],
        rules=[
            "Keep workflows readable and scoped to the repository needs.",
            "Use pinned or trusted actions when possible.",
            "Avoid exposing secrets in logs.",
            "Prefer caching only when it improves CI time without hiding failures.",
        ],
    ),
}
