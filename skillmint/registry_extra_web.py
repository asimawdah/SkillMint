from __future__ import annotations

from .models import StackDefinition


def s(id, name, commands=None, directories=None, avoid=None, rules=None):
    return StackDefinition(id=id, name=name, commands=commands or {}, directories=directories or [], avoid=avoid or [], rules=rules or [])


WEB_REGISTRY = {
    "node": s("node", "Node.js / JavaScript / TypeScript", {"Install dependencies": "npm install", "Dev server": "npm run dev", "Build": "npm run build", "Test": "npm test"}, ["src/", "test/", "scripts/"], ["node_modules/", "dist/", "build/"], ["Use the package manager already used by the project.", "Prefer TypeScript when the project already uses it."]),
    "nextjs": s("nextjs", "Next.js", {"Install dependencies": "npm install", "Dev server": "npm run dev", "Build": "npm run build"}, ["app/", "pages/", "components/", "public/"], [".next/", "node_modules/", "out/"], ["Follow the router already used by the project.", "Keep server and client component boundaries explicit."]),
    "vue": s("vue", "Vue", {"Install dependencies": "npm install", "Dev server": "npm run dev", "Build": "npm run build"}, ["src/", "components/", "views/"], ["node_modules/", "dist/"], ["Follow Vue single-file component conventions."]),
    "nuxt": s("nuxt", "Nuxt", {"Install dependencies": "npm install", "Dev server": "npm run dev", "Build": "npm run build"}, ["pages/", "components/", "server/", "composables/"], ["node_modules/", ".nuxt/", ".output/"], ["Follow Nuxt routing and server directory conventions."]),
    "svelte": s("svelte", "Svelte / SvelteKit", {"Install dependencies": "npm install", "Dev server": "npm run dev", "Build": "npm run build"}, ["src/routes/", "src/lib/", "static/"], ["node_modules/", ".svelte-kit/", "build/"], ["Follow SvelteKit file-based routing conventions when present."]),
    "angular": s("angular", "Angular", {"Install dependencies": "npm install", "Dev server": "ng serve", "Build": "ng build", "Test": "ng test"}, ["src/app/", "src/assets/"], ["node_modules/", "dist/", ".angular/"], ["Follow Angular workspace and component conventions."]),
}
