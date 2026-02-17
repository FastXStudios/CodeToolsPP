import os
from PIL import Image, ImageTk
import tkinter as tk
from utils.helpers import resource_path

class FileIconManager:
    """Gestiona los iconos de archivos según su extensión usando imágenes PNG"""
    
    ICON_MAP = {
        # Programación
        '.py': 'python.png',
        '.js': 'javascript.png',
        '.jsx': 'react.png',
        '.tsx': 'react_ts.png',
        '.ts': 'typescript.png',
        '.java': 'java.png',
        '.cpp': 'cpp.png',
        '.c': 'c.png',
        '.cs': 'csharp.png',
        '.go': 'go.png',
        '.rs': 'rust.png',
        '.php': 'php.png',
        '.rb': 'ruby.png',
        '.swift': 'swift.png',
        '.kt': 'kotlin.png',
        '.scala': 'scala.png',
        '.r': 'r.png',
        '.lua': 'lua.png',
        '.pl': 'perl.png',
        '.groovy': 'groovy.png',
        '.dart': 'dart.png',
        '.v': 'vlang.png',
        '.zig': 'zig.png',
        '.nim': 'nim.png',
        '.cr': 'crystal.png',
        '.ex': 'elixir.png',
        '.exs': 'elixir.png',
        '.elm': 'elm.png',
        '.erl': 'erlang.png',
        '.hrl': 'erlang.png',
        '.clj': 'clojure.png',
        '.cljs': 'clojure.png',
        '.fs': 'fsharp.png',
        '.fsx': 'fsharp.png',
        '.hs': 'haskell.png',
        '.ml': 'ocaml.png',
        '.mli': 'ocaml.png',
        '.rkt': 'racket.png',
        '.scm': 'scheme.png',
        '.lisp': 'lisp.png',
        '.jl': 'julia.png',
        '.m': 'matlab.png',
        '.pas': 'pascal.png',
        '.for': 'fortran.png',
        '.f90': 'fortran.png',
        '.cob': 'cobol.png',
        '.ada': 'ada.png',
        '.tcl': 'tcl.png',
        '.vala': 'vala.png',
        '.sol': 'solidity.png',
        '.cairo': 'cairo.png',
        '.hack': 'hack.png',
        '.odin': 'odin.png',
        '.mojo': 'mojo.png',
        '.gleam': 'gleam.png',
        '.grain': 'grain.png',
        '.imba': 'imba.png',
        '.res': 'rescript.png',
        '.resi': 'rescript-interface.png',
        '.purs': 'purescript.png',
        '.re': 'reason.png',
        '.rei': 'reason.png',
        '.bal': 'ballerina.png',
        
        # Web
        '.html': 'html.png',
        '.htm': 'html.png',
        '.css': 'css.png',
        '.scss': 'sass.png',
        '.sass': 'sass.png',
        '.less': 'less.png',
        '.styl': 'stylus.png',
        '.vue': 'vue.png',
        '.svelte': 'svelte.png',
        '.astro': 'astro.png',
        '.mjs': 'javascript.png',
        '.cjs': 'javascript.png',
        
        # Datos y configuración
        '.json': 'json.png',
        '.json5': 'json.png',
        '.jsonc': 'json.png',
        '.xml': 'xml.png',
        '.yaml': 'yaml.png',
        '.yml': 'yaml.png',
        '.toml': 'toml.png',
        '.ini': 'settings.png',
        '.cfg': 'settings.png',
        '.conf': 'settings.png',
        '.csv': 'table.png',
        '.tsv': 'table.png',
        '.env': 'env.png',
        '.properties': 'settings.png',
        
        # Documentación
        '.md': 'markdown.png',
        '.mdx': 'mdx.png',
        '.markdown': 'markdown.png',
        '.txt': 'txt.png',
        '.txt': 'text.png',  # O 'txt.png' si así se llama tu archivo
        '.pdf': 'pdf.png',
        '.doc': 'word.png',
        '.docx': 'word.png',
        '.rtf': 'document.png',
        '.tex': 'tex.png',
        '.adoc': 'asciidoc.png',
        '.rst': 'document.png',
        
        # Imágenes
        '.png': 'image.png',
        '.jpg': 'image.png',
        '.jpeg': 'image.png',
        '.gif': 'image.png',
        '.svg': 'svg.png',
        '.ico': 'ico.png',
        '.webp': 'image.png',
        '.bmp': 'image.png',
        '.tiff': 'image.png',
        '.psd': 'adobe-photoshop.png',
        '.ai': 'adobe-illustrator.png',
        '.sketch': 'sketch.png',
        '.fig': 'figma.png',
        '.xd': 'adobe-photoshop.png',
        '.drawio': 'drawio.png',
        
        # Multimedia
        '.mp3': 'audio.png',
        '.wav': 'audio.png',
        '.ogg': 'audio.png',
        '.flac': 'audio.png',
        '.m4a': 'audio.png',
        '.mp4': 'video.png',
        '.avi': 'video.png',
        '.mov': 'video.png',
        '.mkv': 'video.png',
        '.webm': 'video.png',
        '.flv': 'video.png',
        
        # Comprimidos
        '.zip': 'zip.png',
        '.rar': 'zip.png',
        '.7z': 'zip.png',
        '.tar': 'zip.png',
        '.gz': 'zip.png',
        '.bz2': 'zip.png',
        '.xz': 'zip.png',
        
        # Build tools y configuración
        '.gradle': 'gradle.png',
        '.maven': 'maven.png',
        '.mk': 'makefile.png',
        '.cmake': 'cmake.png',
        
        # TypeScript
        '.d.ts': 'typescript-def.png',
        '.map': 'code.png',
        
        # Scripts
        '.sh': 'console.png',
        '.bash': 'console.png',
        '.zsh': 'console.png',
        '.fish': 'console.png',
        '.bat': 'console.png',
        '.cmd': 'console.png',
        '.ps1': 'powershell.png',
        
        # Ejecutables y binarios
        '.exe': 'exe.png',
        '.dll': 'dll.png',
        '.so': 'lib.png',
        '.dylib': 'lib.png',
        '.jar': 'jar.png',
        '.class': 'javaclass.png',
        
        # Templates
        '.hbs': 'handlebars.png',
        '.ejs': 'ejs.png',
        '.pug': 'pug.png',
        '.jade': 'pug.png',
        '.twig': 'twig.png',
        '.njk': 'nunjucks.png',
        '.liquid': 'liquid.png',
        '.mustache': 'template.png',
        '.jinja': 'jinja.png',
        '.jinja2': 'jinja.png',
        
        # Configs de frameworks
        'package.json': 'nodejs.png',
        'package-lock.json': 'npm.png',
        'yarn.lock': 'yarn.png',
        'pnpm-lock.yaml': 'pnpm.png',
        'bun.lockb': 'bun.png',
        'requirements.txt': 'python.png',
        'Pipfile': 'python.png',
        'Pipfile.lock': 'python.png',
        'poetry.lock': 'poetry.png',
        'pyproject.toml': 'python.png',
        'Cargo.toml': 'rust.png',
        'Cargo.lock': 'rust.png',
        'go.mod': 'go.png',
        'go.sum': 'go.png',
        'composer.json': 'php.png',
        'composer.lock': 'php.png',
        'Gemfile': 'ruby.png',
        'Gemfile.lock': 'ruby.png',
        'pom.xml': 'maven.png',
        'build.gradle': 'gradle.png',
        'settings.gradle': 'gradle.png',
        
        # Archivos de configuración específicos
        'tsconfig.json': 'tsconfig.png',
        'jsconfig.json': 'jsconfig.png',
        'webpack.config.js': 'webpack.png',
        'vite.config.js': 'vite.png',
        'vite.config.ts': 'vite.png',
        'rollup.config.js': 'rollup.png',
        'gulpfile.js': 'gulp.png',
        'gruntfile.js': 'grunt.png',
        'next.config.js': 'next.png',
        'next.config.mjs': 'next.png',
        'nuxt.config.js': 'nuxt.png',
        'nuxt.config.ts': 'nuxt.png',
        'astro.config.mjs': 'astro-config.png',
        'svelte.config.js': 'svelte.png',
        'remix.config.js': 'remix.png',
        'gatsby-config.js': 'gatsby.png',
        'angular.json': 'angular.png',
        'nest-cli.json': 'nest.png',
        'deno.json': 'deno.png',
        'deno.jsonc': 'deno.png',
        
        # Linters y formatters
        '.eslintrc': 'eslint.png',
        '.eslintrc.js': 'eslint.png',
        '.eslintrc.json': 'eslint.png',
        '.eslintignore': 'eslint.png',
        'eslint.config.js': 'eslint.png',
        '.prettierrc': 'prettier.png',
        '.prettierrc.json': 'prettier.png',
        '.prettierignore': 'prettier.png',
        'prettier.config.js': 'prettier.png',
        '.stylelintrc': 'stylelint.png',
        '.stylelintrc.json': 'stylelint.png',
        '.editorconfig': 'editorconfig.png',
        'biome.json': 'biome.png',
        '.php-cs-fixer.php': 'php-cs-fixer.png',
        'phpstan.neon': 'phpstan.png',
        'phpunit.xml': 'phpunit.png',
        'rubocop.yml': 'rubocop.png',
        
        # Git
        '.gitignore': 'git.png',
        '.gitattributes': 'git.png',
        '.gitmodules': 'git.png',
        '.gitkeep': 'git.png',
        
        # Docker
        'Dockerfile': 'docker.png',
        'docker-compose.yml': 'docker.png',
        'docker-compose.yaml': 'docker.png',
        '.dockerignore': 'docker.png',
        
        # CI/CD
        '.travis.yml': 'travis.png',
        'azure-pipelines.yml': 'azure-pipelines.png',
        'appveyor.yml': 'appveyor.png',
        'circle.yml': 'circleci.png',
        'circleci.yml': 'circleci.png',
        '.gitlab-ci.yml': 'gitlab.png',
        'jenkinsfile': 'jenkins.png',
        'Jenkinsfile': 'jenkins.png',
        '.drone.yml': 'drone.png',
        'netlify.toml': 'netlify.png',
        'vercel.json': 'vercel.png',
        
        # Testing
        'jest.config.js': 'jest.png',
        'jest.config.ts': 'jest.png',
        'vitest.config.js': 'vitest.png',
        'vitest.config.ts': 'vitest.png',
        'cypress.config.js': 'cypress.png',
        'playwright.config.js': 'playwright.png',
        'karma.conf.js': 'karma.png',
        '.mocharc.json': 'mocha.png',
        
        # Otros archivos importantes
        'README.md': 'readme.png',
        'LICENSE': 'license.png',
        'CHANGELOG.md': 'changelog.png',
        'CONTRIBUTING.md': 'contributing.png',
        'AUTHORS': 'authors.png',
        'CODEOWNERS': 'codeowners.png',
        'CODE_OF_CONDUCT.md': 'conduct.png',
        '.nvmrc': 'nodejs.png',
        '.node-version': 'nodejs.png',
        '.ruby-version': 'ruby.png',
        '.python-version': 'python.png',
        'renovate.json': 'renovate.png',
        'dependabot.yml': 'dependabot.png',
        'turbo.json': 'turborepo.png',
        'nx.json': 'nx.png',
        'lerna.json': 'lerna.png',
        '.huskyrc': 'husky.png',
        'lefthook.yml': 'lefthook.png',
        '.commitlintrc': 'commitlint.png',
        'wrangler.toml': 'wrangler.png',
        'tailwind.config.js': 'tailwindcss.png',
        'postcss.config.js': 'postcss.png',
        'babel.config.js': 'babel.png',
        '.babelrc': 'babel.png',
        'serverless.yml': 'serverless.png',
        'prisma.schema': 'prisma.png',
        'drizzle.config.ts': 'drizzle.png',
        'supabase.config.js': 'supabase.png',
        'firebase.json': 'firebase.png',
        '.firebaserc': 'firebase.png',
        'terraform.tfvars': 'terraform.png',
        '.tf': 'terraform.png',
        '.tfvars': 'terraform.png',
        'ansible.cfg': 'ansible.png',
        'Vagrantfile': 'vagrant.png',
        'justfile': 'just.png',
        'Taskfile.yml': 'taskfile.png',
        'Makefile': 'makefile.png',
        'makefile': 'makefile.png',
    }
    
    FOLDER_ICONS = {
        # Por defecto
        'default': 'folder.png',
        'open': 'folder-open.png',
        
        # Carpetas comunes de desarrollo
        'node_modules': 'folder-node.png',
        'venv': 'folder-python.png',
        '.venv': 'folder-python.png',
        'env': 'folder-environment.png',
        '__pycache__': 'folder-python.png',
        'dist': 'folder-dist.png',
        'build': 'folder-dist.png',
        'out': 'folder-dist.png',
        'output': 'folder-export.png',
        'target': 'folder-target.png',
        'bin': 'folder-dist.png',
        'lib': 'folder-lib.png',
        'libs': 'folder-lib.png',
        'vendor': 'folder-packages.png',
        'packages': 'folder-packages.png',
        
        # Control de versiones
        '.git': 'folder-git.png',
        '.github': 'folder-github.png',
        '.gitlab': 'folder-gitlab.png',
        '.gitea': 'folder-gitea.png',
        '.forgejo': 'folder-forgejo.png',
        '.hg': 'folder-mercurial.png',
        
        # IDEs
        '.vscode': 'folder-vscode.png',
        '.idea': 'folder-intellij.png',
        '.atom': 'folder-atom.png',
        '.sublime': 'folder-sublime.png',
        
        # Frameworks y librerías
        'src': 'folder-src.png',
        'source': 'folder-src.png',
        'app': 'folder-app.png',
        'public': 'folder-public.png',
        'static': 'folder-public.png',
        'assets': 'folder-images.png',
        'images': 'folder-images.png',
        'img': 'folder-images.png',
        'pics': 'folder-images.png',
        'pictures': 'folder-images.png',
        'icons': 'folder-favicon.png',
        'fonts': 'folder-font.png',
        'audio': 'folder-audio.png',
        'video': 'folder-video.png',
        'videos': 'folder-video.png',
        'media': 'folder-images.png',
        
        # Documentación
        'docs': 'folder-docs.png',
        'doc': 'folder-docs.png',
        'documentation': 'folder-docs.png',
        'examples': 'folder-examples.png',
        'samples': 'folder-examples.png',
        
        # Testing
        'test': 'folder-test.png',
        'tests': 'folder-test.png',
        '__tests__': 'folder-test.png',
        'spec': 'folder-test.png',
        'specs': 'folder-test.png',
        'e2e': 'folder-test.png',
        'integration': 'folder-test.png',
        'unit': 'folder-test.png',
        'coverage': 'folder-coverage.png',
        
        # Configuración
        'config': 'folder-config.png',
        'configs': 'folder-config.png',
        'configuration': 'folder-config.png',
        'settings': 'folder-config.png',
        '.config': 'folder-config.png',
        
        # Scripts
        'scripts': 'folder-scripts.png',
        'script': 'folder-scripts.png',
        'tools': 'folder-tools.png',
        'utilities': 'folder-utils.png',
        'utils': 'folder-utils.png',
        'helpers': 'folder-helper.png',
        'helper': 'folder-helper.png',
        
        # Backend
        'api': 'folder-api.png',
        'apis': 'folder-api.png',
        'server': 'folder-server.png',
        'servers': 'folder-server.png',
        'backend': 'folder-server.png',
        'routes': 'folder-routes.png',
        'router': 'folder-routes.png',
        'controllers': 'folder-controller.png',
        'controller': 'folder-controller.png',
        'models': 'folder-database.png',
        'model': 'folder-database.png',
        'services': 'folder-api.png',
        'service': 'folder-api.png',
        'middleware': 'folder-middleware.png',
        'middlewares': 'folder-middleware.png',
        'handlers': 'folder-controller.png',
        'resolvers': 'folder-resolver.png',
        'graphql': 'folder-graphql.png',
        
        # Frontend
        'components': 'folder-components.png',
        'component': 'folder-components.png',
        'views': 'folder-views.png',
        'view': 'folder-views.png',
        'pages': 'folder-views.png',
        'page': 'folder-views.png',
        'screens': 'folder-views.png',
        'layouts': 'folder-layout.png',
        'layout': 'folder-layout.png',
        'templates': 'folder-template.png',
        'template': 'folder-template.png',
        'styles': 'folder-css.png',
        'css': 'folder-css.png',
        'sass': 'folder-sass.png',
        'scss': 'folder-sass.png',
        'less': 'folder-less.png',
        'stylus': 'folder-stylus.png',
        
        # Estado y store
        'store': 'folder-store.png',
        'stores': 'folder-store.png',
        'redux': 'folder-redux-reducer.png',
        'reducers': 'folder-redux-reducer.png',
        'actions': 'folder-redux-reducer.png',
        'state': 'folder-ngrx-store.png',
        'vuex': 'folder-vuex-store.png',
        'ngrx': 'folder-ngrx-store.png',
        
        # Base de datos
        'database': 'folder-database.png',
        'db': 'folder-database.png',
        'data': 'folder-database.png',
        'migrations': 'folder-migrations.png',
        'migration': 'folder-migrations.png',
        'seeds': 'folder-seeders.png',
        'seeders': 'folder-seeders.png',
        'fixtures': 'folder-database.png',
        
        # Docker y containerización
        'docker': 'folder-docker.png',
        '.docker': 'folder-docker.png',
        'kubernetes': 'folder-kubernetes.png',
        'k8s': 'folder-kubernetes.png',
        'helm': 'folder-helm.png',
        
        # Cloud
        'aws': 'folder-aws.png',
        'azure': 'folder-azure-pipelines.png',
        'gcp': 'folder-api.png',
        'terraform': 'folder-terraform.png',
        'serverless': 'folder-serverless.png',
        'lambda': 'folder-aws.png',
        'functions': 'folder-functions.png',
        
        # CI/CD
        'workflows': 'folder-gh-workflows.png',
        '.circleci': 'folder-circleci.png',
        'jenkins': 'folder-ci.png',
        'ci': 'folder-ci.png',
        'pipelines': 'folder-ci.png',
        
        # Mobile
        'android': 'folder-android.png',
        'ios': 'folder-ios.png',
        'mobile': 'folder-mobile.png',
        
        # Frameworks específicos
        'angular': 'folder-angular.png',
        'react': 'folder-react-components.png',
        'vue': 'folder-vue.png',
        'svelte': 'folder-svelte.png',
        'next': 'folder-next.png',
        'nuxt': 'folder-nuxt.png',
        'astro': 'folder-astro.png',
        'django': 'folder-python.png',
        'flask': 'folder-python.png',
        'laravel': 'folder-php.png',
        'symfony': 'folder-php.png',
        'rails': 'folder-ruby.png',
        'spring': 'folder-java.png',
        
        # Otros
        'temp': 'folder-temp.png',
        'tmp': 'folder-temp.png',
        'cache': 'folder-temp.png',
        '.cache': 'folder-temp.png',
        'logs': 'folder-log.png',
        'log': 'folder-log.png',
        'backup': 'folder-backup.png',
        'backups': 'folder-backup.png',
        'archive': 'folder-archive.png',
        'archives': 'folder-archive.png',
        'downloads': 'folder-download.png',
        'upload': 'folder-upload.png',
        'uploads': 'folder-upload.png',
        'private': 'folder-private.png',
        'secure': 'folder-secure.png',
        'trash': 'folder-trash.png',
        'i18n': 'folder-i18n.png',
        'locales': 'folder-i18n.png',
        'locale': 'folder-i18n.png',
        'translations': 'folder-i18n.png',
        'hooks': 'folder-hook.png',
        'plugins': 'folder-plugin.png',
        'plugin': 'folder-plugin.png',
        'modules': 'folder-packages.png',
        'module': 'folder-packages.png',
        'types': 'folder-typescript.png',
        'typings': 'folder-typescript.png',
        '@types': 'folder-typescript.png',
        'interfaces': 'folder-interface.png',
        'enums': 'folder-enum.png',
        'constants': 'folder-constant.png',
        'guards': 'folder-guard.png',
        'pipes': 'folder-pipe.png',
        'filters': 'folder-filter.png',
        'directives': 'folder-directive.png',
        'decorators': 'folder-decorators.png',
        'core': 'folder-core.png',
        'shared': 'folder-shared.png',
        'common': 'folder-shared.png',
        'features': 'folder-features.png',
        'feature': 'folder-features.png',
        'repositories': 'folder-repository.png',
        'repository': 'folder-repository.png',
        'entities': 'folder-database.png',
        'dto': 'folder-interface.png',
        'dtos': 'folder-interface.png',
        'schemas': 'folder-database.png',
        'schema': 'folder-database.png',
        'tasks': 'folder-tasks.png',
        'jobs': 'folder-job.png',
        'queues': 'folder-queue.png',
        'queue': 'folder-queue.png',
        'events': 'folder-event.png',
        'listeners': 'folder-event.png',
        'providers': 'folder-api.png',
        'validators': 'folder-api.png',
        'validation': 'folder-api.png',
        'errors': 'folder-error.png',
        'exceptions': 'folder-error.png',
        'ui': 'folder-ui.png',
        'ux': 'folder-ui.png',
        'design': 'folder-ui.png',
        'theme': 'folder-theme.png',
        'themes': 'folder-theme.png',
        'contexts': 'folder-context.png',
        'context': 'folder-context.png',
        'prisma': 'folder-prisma.png',
        'drizzle': 'folder-drizzle.png',
        'supabase': 'folder-supabase.png',
        'firebase': 'folder-firebase.png',
        'firestore': 'folder-firestore.png',
        'vercel': 'folder-vercel.png',
        'netlify': 'folder-netlify.png',
        'storybook': 'folder-storybook.png',
        '.storybook': 'folder-storybook.png',
        'cypress': 'folder-cypress.png',
        'husky': 'folder-husky.png',
        '.husky': 'folder-husky.png',
        'eslint': 'folder-eslint.png',
        'webpack': 'folder-webpack.png',
        'turbo': 'folder-turborepo.png',
        '.turbo': 'folder-turborepo.png',
        'monorepo': 'folder-packages.png',
        'workspace': 'folder-packages.png',
        'workspaces': 'folder-packages.png',
        'lerna': 'folder-packages.png',
        'nx': 'folder-packages.png',
        'pnpm': 'folder-packages.png',
        'yarn': 'folder-yarn.png',
        'npm': 'folder-packages.png',
        'bun': 'folder-packages.png',
        'proto': 'folder-proto.png',
        'protos': 'folder-proto.png',
        'grpc': 'folder-proto.png',
        'animations': 'folder-animation.png',
        'animation': 'folder-animation.png',
        'lottie': 'folder-lottie.png',
        'svg': 'folder-svg.png',
        'pdf': 'folder-pdf.png',
        'unity': 'folder-unity.png',
        'godot': 'folder-godot.png',
        'blender': 'folder-blender.png',
        'shaders': 'folder-shader.png',
        'shader': 'folder-shader.png',
        'pytorch': 'folder-pytorch.png',
        'jupyter': 'folder-jupyter.png',
        'notebooks': 'folder-jupyter.png',
        'prompts': 'folder-prompts.png',
        'claude': 'folder-claude.png',
        '.claude': 'folder-claude.png',
        'cline': 'folder-cline.png',
        '.cline': 'folder-cline.png',
        'cursor': 'folder-cursor.png',
        '.cursor': 'folder-cursor.png',
        'contracts': 'folder-contract.png',
        'contract': 'folder-contract.png',
        'tauri': 'folder-src-tauri.png',
        'desktop': 'folder-desktop.png',
        'expo': 'folder-expo.png',
        'flutter': 'folder-flutter.png',
        'fastlane': 'folder-fastlane.png',
        'resources': 'folder-resource.png',
        'res': 'folder-resource.png',
        'content': 'folder-content.png',
        'posts': 'folder-content.png',
        'blog': 'folder-content.png',
        'articles': 'folder-content.png',
    }
    
    def __init__(self, icon_path=None):
        self.icon_path = icon_path or resource_path("assets/icons")
        self.cache = {}
        self.default_size = (20, 20)
        
        # Crear placeholder si no existen los iconos
        self._create_placeholder_icons()
    
    def _create_placeholder_icons(self):
        """Crea iconos placeholder si no existen"""
        os.makedirs(self.icon_path, exist_ok=True)
        
        # Lista de iconos esenciales
        essential_icons = [
            'file.png', 'folder.png', 'folder-open.png'
        ]
        
        for icon_name in essential_icons:
            icon_file = os.path.join(self.icon_path, icon_name)
            if not os.path.exists(icon_file):
                # Crear icono placeholder simple
                img = Image.new('RGBA', (20, 20), (100, 100, 100, 255))
                img.save(icon_file)
    
    def load_icon(self, icon_name, size=None):
        """Carga un icono PNG"""
        if size is None:
            size = self.default_size
        
        cache_key = f"{icon_name}_{size[0]}x{size[1]}"
        
        if cache_key in self.cache:

            return self.cache[cache_key]
        
        try:
            icon_file = os.path.join(self.icon_path, icon_name)

            
            if not os.path.exists(icon_file):
                icon_file = os.path.join(self.icon_path, 'file.png')
            
            if os.path.exists(icon_file):
                img = Image.open(icon_file)
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.cache[cache_key] = photo
                return photo
            else:
                # Crear icono placeholder en memoria
                img = Image.new('RGBA', size, (100, 100, 100, 255))
                photo = ImageTk.PhotoImage(img)
                self.cache[cache_key] = photo
                return photo
                
        except Exception as e:
            print(f"❌ ERROR load_icon: {e}")
            # Retornar placeholder
            img = Image.new('RGBA', size, (100, 100, 100, 255))
            photo = ImageTk.PhotoImage(img)
            return photo
    
    def get_file_icon(self, filename, size=None):
        """Obtiene el icono para un archivo"""
        filename_lower = filename.lower()
        
        # 1. Primero verificar por nombre completo
        if filename_lower in self.ICON_MAP:
            icon_name = self.ICON_MAP[filename_lower]
            return self.load_icon(icon_name, size)
        
        # 2. Buscar patrones específicos en el nombre (ej: .controller.ts, .service.ts)
        # Archivos .controller.ts/js/tsx/jsx
        if '.controller.' in filename_lower:
            return self.load_icon('controller.png', size)
        
        # Archivos .service.ts/js/tsx/jsx
        if '.service.' in filename_lower:
            return self.load_icon('services.png', size)
        
        # Archivos .routes.ts/js o .route.ts/js
        if '.route' in filename_lower and ('routes.' in filename_lower or 'route.' in filename_lower):
            return self.load_icon('routing.png', size)
        
        # Archivos .model.ts/js
        if '.model.' in filename_lower:
            return self.load_icon('database.png', size)
        
        # Archivos .entity.ts/js
        if '.entity.' in filename_lower:
            return self.load_icon('database.png', size)
        
        # Archivos .middleware.ts/js
        if '.middleware.' in filename_lower:
            return self.load_icon('settings.png', size)
        
        # Archivos .guard.ts/js
        if '.guard.' in filename_lower:
            return self.load_icon('lock.png', size)
        
        # Archivos .pipe.ts/js
        if '.pipe.' in filename_lower:
            return self.load_icon('filter.png', size)
        
        # Archivos .decorator.ts/js
        if '.decorator.' in filename_lower:
            return self.load_icon('settings.png', size)
        
        # Archivos .dto.ts/js
        if '.dto.' in filename_lower:
            return self.load_icon('interface.png', size)
        
        # Archivos .interface.ts/js
        if '.interface.' in filename_lower:
            return self.load_icon('typescript-def.png', size)
        
        # Archivos .type.ts o .types.ts
        if ('.type.' in filename_lower or '.types.' in filename_lower):
            return self.load_icon('typescript-def.png', size)
        
        # Archivos .constant.ts/js o .constants.ts/js
        if ('.constant.' in filename_lower or '.constants.' in filename_lower):
            return self.load_icon('code.png', size)
        
        # Archivos .util.ts/js, .utils.ts/js, .helper.ts/js
        if any(pattern in filename_lower for pattern in ['.util.', '.utils.', '.helper.']):
            return self.load_icon('code.png', size)
        
        # Archivos .validator.ts/js
        if '.validator.' in filename_lower:
            return self.load_icon('code.png', size)
        
        # Archivos .repository.ts/js
        if '.repository.' in filename_lower:
            return self.load_icon('database.png', size)
        
        # Archivos .resolver.ts/js (GraphQL)
        if '.resolver.' in filename_lower:
            return self.load_icon('graphql.png', size)
        
        # Archivos .schema.ts/js
        if '.schema.' in filename_lower:
            return self.load_icon('database.png', size)
        
        # Archivos .test.ts/js/tsx/jsx o .spec.ts/js/tsx/jsx
        if '.test.' in filename_lower or '.spec.' in filename_lower:
            if '.ts' in filename_lower:
                if '.tsx' in filename_lower:
                    return self.load_icon('test-tsx.png', size)
                return self.load_icon('test-ts.png', size)
            elif '.js' in filename_lower:
                if '.jsx' in filename_lower:
                    return self.load_icon('test-jsx.png', size)
                return self.load_icon('test-js.png', size)
        
        # Archivos .config.ts/js
        if '.config.' in filename_lower:
            return self.load_icon('settings.png', size)
        
        # Archivos .module.ts/js
        if '.module.' in filename_lower:
            return self.load_icon('code.png', size)
        
        # Archivos .stories.ts/tsx/js/jsx o .story.ts/tsx/js/jsx
        if '.stories.' in filename_lower or '.story.' in filename_lower:
            return self.load_icon('storybook.png', size)
        
        # 3. Por último, buscar por extensión simple
        ext = os.path.splitext(filename)[1].lower()
        icon_name = self.ICON_MAP.get(ext, 'file.png')
        return self.load_icon(icon_name, size)

    def get_folder_icon(self, folder_name, is_open=False, size=None):
        """Obtiene el icono para una carpeta"""
        folder_lower = folder_name.lower()
        
        # Carpetas especiales
        if folder_lower in self.FOLDER_ICONS:
            icon_name = self.FOLDER_ICONS[folder_lower]
            # Agregar sufijo -open si está abierta (para carpetas normales)
            if is_open and icon_name in ['folder.png']:
                icon_name = 'folder_open.png'
            elif is_open and 'folder-' in icon_name and not icon_name.endswith('-open.png'):
                # Intentar versión open
                open_icon = icon_name.replace('.png', '-open.png')
                if os.path.exists(os.path.join(self.icon_path, open_icon)):
                    icon_name = open_icon
            return self.load_icon(icon_name, size)
        
        # Carpeta normal
        icon_name = 'folder_open.png' if is_open else 'folder.png'
        return self.load_icon(icon_name, size)
    
    def is_warning_folder(self, folder_name):
        """Verifica si es una carpeta que debería generar alerta"""
        warning_folders = [
            'node_modules', 'venv', '.venv', 'env', '__pycache__', 
            '.git', 'dist', 'build', 'vendor', 'target', 'cache',
            '.cache', 'temp', 'tmp'
        ]
        return folder_name.lower() in warning_folders
