from __future__ import annotations

from .models import StackDefinition
from .registry_extra import EXTRA_REGISTRY

REGISTRY = {
    "flutter": StackDefinition(id="flutter", name="Flutter / Dart", commands={"Install dependencies": "flutter pub get", "Analyze": "flutter analyze", "Test": "flutter test", "Run": "flutter run"}, directories=["lib/", "test/", "android/", "ios/", "web/"], avoid=["build/", ".dart_tool/"], rules=["Follow Flutter and Dart conventions."]),
    "react": StackDefinition(id="react", name="React", commands={"Install dependencies": "npm install", "Dev server": "npm run dev", "Build": "npm run build", "Test": "npm test"}, directories=["src/", "public/", "components/", "pages/", "app/"], avoid=["node_modules/", "dist/", "build/", ".next/"], rules=["Keep components focused and reusable."]),
    "python": StackDefinition(id="python", name="Python", commands={"Install dependencies": "pip install -r requirements.txt", "Test": "pytest"}, directories=["src/", "tests/", "app/"], avoid=[".venv/", "__pycache__/"], rules=["Follow the existing Python style and project layout."]),
    "fastapi": StackDefinition(id="fastapi", name="FastAPI", commands={"Run API": "uvicorn main:app --reload", "Test": "pytest"}, directories=["app/", "routers/", "tests/"], avoid=[".venv/", "__pycache__/"], rules=["Use routers and dependency injection where appropriate."]),
    "django": StackDefinition(id="django", name="Django", commands={"Run server": "python manage.py runserver", "Migrate": "python manage.py migrate", "Test": "python manage.py test"}, directories=["apps/", "templates/", "static/"], avoid=[".venv/", "__pycache__/"], rules=["Follow Django conventions."]),
    "laravel": StackDefinition(id="laravel", name="Laravel / PHP", commands={"Install dependencies": "composer install", "Run server": "php artisan serve", "Test": "php artisan test"}, directories=["app/", "routes/", "database/migrations/"], avoid=["vendor/", ".env"], rules=["Follow Laravel conventions."]),
    "go": StackDefinition(id="go", name="Go", commands={"Download dependencies": "go mod download", "Run tests": "go test ./...", "Build": "go build ./..."}, directories=["cmd/", "internal/", "pkg/"], avoid=["bin/", "dist/"], rules=["Follow idiomatic Go conventions."]),
    "docker": StackDefinition(id="docker", name="Docker", commands={"Build image": "docker build .", "Compose up": "docker compose up -d"}, directories=[], avoid=["volumes/", ".docker/"], rules=["Keep Dockerfiles minimal and reproducible."]),
    "github-actions": StackDefinition(id="github-actions", name="GitHub Actions", commands={}, directories=[".github/workflows/"], avoid=[], rules=["Keep workflows readable and scoped."]),
}
REGISTRY.update(EXTRA_REGISTRY)
