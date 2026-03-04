# 📦 Proyecto Licium: Módulos Personalizados

Este proyecto contiene un conjunto de módulos desarrollados para el framework **Licium**. Actualmente, el repositorio aloja múltiples módulos diseñados para extender de manera natural las amplias capacidades del sistema base: **Checklists Prácticos (`practice_checklist`)**, **Gestión de Préstamos de Activos (`asset_lending`)**, y un tercer módulo en actual etapa de concepción destinado a la **Moderación de Feedback (`feedback_moderation`)**.

---

## 🏗 Arquitectura General del Proyecto

El proyecto está diseñado bajo una robusta arquitectura modular. El **Backend**, apoyado en FastAPI, expone una API REST moderna y se apoya en una base de datos **PostgreSQL** para la persistencia. Por otro lado, un **Frontend** reactivo y desacoplado, construido sobre Nuxt.js, consume estos puntos de entrada. Todos los módulos que se detallan a continuación extienden el núcleo (core) de la aplicación inyectándose de manera totalmente dinámica en tiempo de ejecución.

```mermaid
graph TD
    Client[Cliente / Navegador] -->|HTTP / API REST| Frontend(Frontend Nuxt.js)
    Frontend -->|HTTP / API REST| API(Backend API - Licium Base)
    
    subgraph Módulos Dinámicos
    API <--> PC[Checklists<br/>practice_checklist]
    API <--> AL[Gestión de Préstamos<br/>asset_lending]
    API <--> FM[Moderación de Feedback<br/>feedback_moderation]
    end

    API --> DB[(Base de Datos PostgreSQL)]
```

---

## 📂 Estructura General del Repositorio

La estructura de carpetas a nivel raíz contiene la configuración local indispensable de los servicios, siendo la carpeta clave `modules/` donde radican los proyectos propios.

```text
modulo-checkList/
├── docker-compose.backend-dev.yml  # Configuración integral de los servicios en Docker
├── filestore/                      # Almacenamiento local persistente de archivos generados y logs
└── modules/                        # ➔ Directorio raíz de los submódulos de la aplicación
    ├── practice_checklist/         # Proyecto 1: Módulo de Checklists (Principal)
    ├── asset_lending/              # Proyecto 2: Módulo de Gestión de Activos y Préstamos
    └── feedback_moderation/        # Proyecto 3: Módulo de Moderación de Feedback
```

---

## 🧩 Detalle de los Proyectos / Módulos

### 📌 Nivel 1: Checklists de Práctica (`practice_checklist`)

Este módulo fue diseñado para gobernar un sistema completo y persistente en el que permite crear, administrar y visualizar **Checklists** completamente estructurados. Cada checklist actúa como un contenedor de múltiples **Tareas (Items)** granulares, lo cual es ideal para realizar auditorías, controles rutinarios (QA) o procesos de validación secuenciales. Además incorpora opciones para mejorar y automatizar el flujo de trabajo, como el cierre automático tras no tener actividad por determinados días.

#### 📂 Estructura Interna y Entidades

```text
practice_checklist/
├── __manifest__.yaml       # Define las dependencias del módulo (depende fuertemente de 'ui'), versión y los ficheros de carga en orden
├── data/                   # Archivos de aprovisionamiento de configuración base
│   ├── acl_rules.yml       # Reglas de las Listas de Control de Acceso (ACLs) y directrices de seguridad
│   ├── groups.yml          # Estructura e inserción por defecto de los Grupos de usuarios
│   └── ui_modules.yml      # Manifiesto que instruye al frontend cómo incluir este ecosistema en la interfaz
├── i18n/                   # Traducciones e internacionalización (es.yml, en.yml) para multilingüismo
├── models/
│   └── checklist.py        # 🗄️ Definición ORM (SQLAlchemy) de los Modelos de Datos.
│                           # Relacionan bases y configuración avanzada bajo una estructura relacional pura.
├── services/
│   └── checklist.py        # ⚙️ Controladores con lógica de negocio o validación transaccional previo al ingreso en BD
└── views/                  # UI del backend para inyectarse al core
    ├── menu.yml            # Árbol de navegación y accesos menú a inyectarse en el Front-End
    └── views.yml           # Declaración y estructura de la organización, de listas y formularios visibles
```

#### 🗄️ Modelos Principales
*   **`PracticeChecklist`**: Entidad maestra del checklist. Almacena campos críticos como `name` (Nombre del checklist), `status` (Borrador, Abierto, Cerrado), `is_public` (visibilidad global) y `owner_id` (Relación M:1 hacia el usuario propietario del checklist).
*   **`PracticeChecklistItem`**: Múltiples actividades dentro del Checklist maestro. Mantiene una clave foránea `checklist_id` y además permite asignar a usuarios específicos (`assigned_user_id`) mediante campos vitales como `title`, notas opcionales (`note`), y estados transaccionales (`is_done`, `done_at`).
*   **`PracticeChecklistSetting`**: Modelo persistente de configuración para dictar reglas automáticas, como booleanos `auto_close` ligados con número de días configurables (`days_to_close`).

---

### 📌 Nivel 2: Gestión de Préstamos (`asset_lending`)

Supervisión, administración de inventarios robustos, y ciclo de vida de préstamos son el pilar de este módulo. Permite censar los distintos activos (`Assets`), establecer y gestionar los espacios físicos definidos como almacenes (`Locations`) para dichos activos y, sobre todo, gobernar centralmente las asignaciones, devoluciones y mora (`Loans`) asociados a cada respectivo usuario.

#### 📂 Estructura Interna y Entidades

```text
asset_lending/
├── __manifest__.yaml       # Identificador base del recurso. Indica versión, nombre técnico y orden preciso de inyecciones (grupos, acls, UI, vistas y menús).
├── models/
│   ├── asset.py            # (Archivos unificados internamente en lending.py)
│   ├── lending.py          # 🗄️ Entidades unificadas relacionadas con toda la gestión: Location, Asset y Loan
│   └── location.py         
├── security/               # Reglas y políticas de seguridad (Access Controls Lists directas)
│   └── access_control.yml
├── services/               # ⚙️ Scripts de lógica interna, handlers y validadores correspondientes a los servicios
│   └── asset_service.py    #         de Locations, Assets, AssetLoans.
└── views/
    ├── menu.yml            # Rutas de entrada a la interfaz (Menús laterales)
    └── views.yml           # Listados, Action windows, y definiciones de plantillas y layouts.
```

#### 🗄️ Modelos Principales
*   **`Location`**: Modela lugares de almacenamiento o depósito físico en el sistema. Almacena su nombre, código único (`code`) y si se encuentra activo o en desuso.
*   **`Asset`**: Base de recursos físicos a ser prestados, definidos por `name`, y clasificados inequívocamente con `asset_code`. Disponen de un control de estado en tiempo real (Disponible, En Préstamo, Mantenimiento) y lógicamente vinculados a ubicaciones `location_id`.
*   **`Loan`**: Archiva todo rastro documental del préstamo realizado entre un usuario y un activo `asset_id`. Comprende variables obligatorias de seguimiento de tiempo como cuándo fue prestado (`checkout_at`), estimación máxima exigible de devolución (`due_at`) y cierre final (`returned_at`), junto con variables semánticas de estado (`status` abierto, devuelto, o atrasado). Permite notas anexas en salida y retorno.

#### ✅ Requisitos Cumplidos

1. **Módulo instalable por CLI**
   * **Dónde está**: En la raíz del módulo (`__manifest__.yaml` y los `__init__.py`).
   * **Cómo se cumple**: Al crear el archivo `__manifest__.yaml` con los metadatos correctos (`name`, `version`, `depends`, y la lista ordenada en `data`), el framework (Licium) reconoce la carpeta como un módulo válido. Esto permite que al ejecutar el comando en la terminal (CLI) el sistema sepa en qué orden debe leer los YAML e inyectarlos en PostgreSQL.
     https://github.com/jesuscb123/modulos-libnamic-practice/blob/85077e575324eded9ab45130eb8cdcd646631e26/modules/asset_lending/__manifest__.yaml#L1-L13

2. **Flujo completo checkout/return probado**
   * **Dónde está**: En `services/lending.py` (clase `AssetLoanService`).
     https://github.com/jesuscb123/modulos-libnamic-practice/blob/85077e575324eded9ab45130eb8cdcd646631e26/modules/asset_lending/services/lending.py#L1-L90
   * **Cómo se cumple**: 
     - **Checkout**: Sobrescribimos el método `create()`. Interceptamos la creación del préstamo, validamos que el recurso esté `available`, le cambiamos el estado a `loaned` para bloquearlo, e inyectamos la fecha actual en `checkout_at`.
       https://github.com/jesuscb123/modulos-libnamic-practice/blob/85077e575324eded9ab45130eb8cdcd646631e26/modules/asset_lending/services/lending.py#L38-L71
     - **Return**: Creamos la función `@exposed_action` llamada `return_asset()`. Esta función busca el préstamo, le pone estado `returned` con su fecha final (`returned_at`), y acto seguido busca el portátil asociado y lo devuelve al estado `available`.
     - https://github.com/jesuscb123/modulos-libnamic-practice/blob/85077e575324eded9ab45130eb8cdcd646631e26/modules/asset_lending/services/lending.py#L73-L90

3. **Vistas admin funcionales**
   * **Dónde está**: En la carpeta `views/` (`views.yml` y `menu.yml`).
   * **Cómo se cumple**: 
     - En `views.yml` definimos las tablas de datos (`ui_view_type_list`) y los formularios (`ui_view_type_form`) para `Location`, `Asset` y `Loan`.
     - Cumplimos la recomendación didáctica añadiendo `chip: true` al campo `status` para que salgan las píldoras de colores, y añadiendo el bloque `row_actions` para que el botón de "Devolver Recurso" aparezca directamente en cada fila de la tabla.
       https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/asset_lending/views/views.yml#L1-L133
     - En `menu.yml` conectamos estas vistas al menú lateral del administrador.
       https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/asset_lending/views/menu.yml#L2-L93

4. **ACL separada por lector/gestor**
   * **Dónde está**: En la carpeta `data/` (`groups.yml` y `acl_rules.yml`).
   * **Cómo se cumple**: 
     - En `groups.yml` creamos la jerarquía: `asset_lending_group_reader` y, heredando de él, el `asset_lending_group_manager`.
       https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/asset_lending/data/groups.yml#L1-L11
     - En `acl_rules.yml` asignamos los permisos reales sobre el comodín `asset_lending.*`: al `reader` solo le dimos `perm_read: true`, mientras que al `manager` le activamos todo (`perm_write`, `perm_create`, `perm_delete`).
       https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/asset_lending/data/acl_rules.yml#L1-L16

---

### 📌 Nivel 3: Moderación de Feedback (`feedback_moderation`)

Este módulo implementa un sistema estructurado de captura, clasificación y moderación de sugerencias y retroalimentación. Está diseñado para que los usuarios puedan aportar ideas (`Suggestions`) y comentarlas (`Comments`), mientras un equipo con rol de moderador aprueba, rechaza o fusiona estas aportaciones antes de hacerlas visibles de forma pública.

#### 📂 Estructura Interna y Entidades

```text
feedback_moderation/
├── __manifest__.yaml       # Define dependencias (requiere 'ui'), versión y orden de carga
├── data/                   # Archivos de aprovisionamiento de configuración base (ACLs, grupos, etc.)
├── models/
│   └── feedback.py         # 🗄️ Definición ORM (SQLAlchemy) de los Modelos (Tag, Suggestion, Comment)
├── services/
│   └── feedback.py         # ⚙️ Servicios y manejadores transaccionales de moderación (publicar, rechazar, fusionar)
└── views/                  # Elementos UI del backend inyectados en el core
    ├── menu.yml            # Vías de navegación en el Front-End
    └── views.yml           # Representación de los formularios y listas
```

#### 🗄️ Modelos Principales
*   **`Suggestion`**: Entidad central que canaliza una idea o reporte. Almacena campos como `title`, `content` y `author_email`, controlando estrictamente su visibilidad mediante un manejador de estados `status` (Pendiente, Publicada, Rechazada, Fusionada) y el boolean `is_public`. Admite notas de revisión `moderation_note` de parte del moderador.
*   **`Comment`**: Aportaciones adicionales y respuestas a una sugerencia específica (`suggestion_id`). Siguen un flujo de moderación idéntico al requerir validación explícita (`status`) previa a su publicación.
*   **`Tag`**: Sistema de categorización ágil (`name`, `slug`, `color`) vinculado de forma Muchos-a-Muchos a las sugerencias, permitiendo agruparlas semánticamente.

#### ✅ Requisitos Cumplidos

1. **Flujo de moderación extremo a extremo**
   * **Dónde está**: En `models/feedback.py` y `services/feedback.py`.
    `models/feedback.py`
     https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/feedback_moderation/models/feedback.py#L1-L74
     `services/feedback.py`
     https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/feedback_moderation/services/feedback.py#L1-L101
   * **Cómo se cumple**: Diseñamos un ciclo de vida completo. Al nacer (sobrescribiendo `create`), la sugerencia se fuerza a `status="pending"` e `is_public=False`. Creamos funciones `@exposed_action` exclusivas para moderadores: `publish`, `reject`, `merge` y `reopen`. Estas funciones cambian los estados, actualizan la visibilidad, registran la nota del moderador (`moderation_note`) y guardan qué usuario tomó la decisión (`reviewed_by_id`).
     
     

2. **ACL pública con domain**
   * **Dónde está**: En `data/acl_rules.yml` (dentro del módulo de feedback).
   * **Cómo se cumple**: Añadimos reglas específicas para el grupo de usuarios anónimos (`core.core_group_public`). Les dimos permiso para crear sugerencias y leerlas, pero limitamos la lectura a nivel de base de datos añadiendo este bloque clave:
     ```yaml
     domain:
       - { field: "status", operator: "=", value: "published" }
       - { field: "is_public", operator: "=", value: true }
     ```
     Esto garantiza que el público general jamás pueda consultar por API un comentario rechazado o pendiente.
     https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/feedback_moderation/data/acl_rules.yml#L1-L31

3. **Acciones de estado con formulario automático**
   * **Dónde está**: En `views/views.yml` (dentro de los `form_actions` de la sugerencia).
   * **Cómo se cumple**: En lugar de programar modales en Vue.js, aprovechamos la potencia del framework declarativo añadiendo la propiedad `params` a nuestros botones de acción. Por ejemplo, en el botón de "Rechazar":
     ```yaml
     params:
       - name: note
         label: "Motivo del rechazo"
         type: string
         required: true
     ```
     Esto le indica al frontend que, al hacer clic, debe levantar automáticamente un formulario emergente pidiendo ese campo antes de enviar la petición al servicio Python.
     https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/feedback_moderation/views/views.yml#L1-L129

4. **Pruebas unitarias de transición de estado**
   * **Dónde está**: En `tests/test_moderation_states.py`.
   * **Cómo se cumple**: Creamos una batería de tests usando `pytest` y la librería `unittest.mock`. Simulamos la capa de base de datos (con `MagicMock` y `@patch`) para aislar nuestra lógica de negocio. Probamos programáticamente que:
     - La creación inicial siempre fuerza el estado a "pendiente".
     - La transición `publish` cambia los booleanos correctamente.
     - La transición `reject` mantiene la sugerencia privada.
     - El sistema lanza un error 400 (`HTTPException`) si se intenta hacer un `merge` de un ID consigo mismo.
       https://github.com/jesuscb123/modulos-libnamic-practice/blob/5ea31bc475a7fd8ac44cde8fa2f318628c73412d/modules/feedback_moderation/tests/test_moderation_states.py#L1-L82

---

## 🚀 Guía Rápida de Despliegue en Entornos de Desarrollo Local (Docker Compose)

El proyecto incluye de manera estandarizada un entorno pre-configurado garantizado y versionado por la infraestructura mediante el empleo de **Docker Compose** en el archivo `docker-compose.backend-dev.yml`. Este utilitario orquesta y levanta la red y todos los contenedores indispensables para correr y aportar modificaciones al sistema directamente con herramientas locales.

### 🛑 Requisitos Previos Necesarios
*Tener instalado **Docker** y el plugin **Docker Compose (v2+)**.*

### ▶️ Puesta en Marcha

1. **Inicie los servicios** corriendo el siguiente comando desde el directorio central de `modulo-checkList`:
   ```bash
   docker-compose -f docker-compose.backend-dev.yml up -d
   ```
2. **Servicios y Entornos expuestos globalmente**:
   * `postgres` (Base de datos relacional): Sirviendo nativamente mediante el puerto local de desarrollo `5432`.
   * `backend` (FastAPI / Motor de Licium Base): Resolviendo en el puerto `8000`. Expone el servidor web API y el backend administrativo, inyectando y montando en tiempo vivo los módulos en la ruta `/opt/licium/modules`.
   * `frontend` (Nuxt.js UI): Activo en el puerto `3000`. Es la interfaz moderna final interactiva conectada por peticiones asincrónicas a la API del backend.
