# El patrón orquestador

[Read in English](orchestrator-pattern.md)

Un agente olvida todo entre sesiones. Lo que sabe de tu proyecto es lo que lee cuando arranca la sesión. Este patrón guarda en disco el conocimiento del proyecto: cómo se trabaja (el proceso) y de qué trata (el dominio), en documentos pequeños que el agente abre solo cuando la tarea los necesita. Dos reglas mantienen esos documentos al día, y las reglas exactas se convierten en scripts.

No depende de ningún agente en particular. Todo son archivos Markdown y scripts dentro de tu repositorio.

## Las piezas

| Pieza | Qué guarda | Cuándo la lee el agente |
|---|---|---|
| `AGENTS.md` en la raíz | El mapa: qué es el proyecto, cómo se trabaja, a dónde ir según la tarea, qué nunca se hace y las dos reglas | Al empezar cada sesión |
| Un README por carpeta | Qué hay en la carpeta y cómo se trabaja ahí | Cuando la tarea toca esa carpeta |
| Skills | Cómo se hace una tarea que se repite, paso a paso, con sus scripts y plantillas | Cuando la tarea coincide con la descripción de la skill |
| Un orquestador | Una skill con una tabla de rutas: qué skill atiende cada tipo de trabajo, qué lee cada etapa y dónde aprueba el usuario | Cuando el trabajo tiene varios tipos o etapas |
| Archivos de estado | En qué punto está el trabajo sin terminar y cuál es el siguiente paso | Cuando una sesión nueva retoma el trabajo |
| Scripts | Las reglas que un programa puede comprobar o aplicar | Nadie tiene que recordarlas: se ejecutan |

```
AGENTS.md (el mapa)
  -> <carpeta>/README.md           cómo se trabaja en esa carpeta
  -> skills/<tarea>/SKILL.md       cómo se hace una tarea repetida
       -> scripts/                 los pasos exactos
  -> skills/<orquestador>/         reparte el trabajo entre las skills
       -> STATUS.md                en qué punto está el trabajo
```

El orquestador decide qué lee cada agente. Una etapa, o un subagente, recibe solo los documentos que indica su ruta más el archivo de estado. Con menos contexto hay menos errores, y cualquier sesión retoma el trabajo donde lo dejó la anterior.

## Las dos reglas

Estas dos líneas van en el mapa. Son las que hacen que el sistema mejore solo en vez de degradarse.

1. **Cuando te corrija, propón en qué documento guardar la lección, enséñame el cambio exacto y espera mi aprobación antes de escribirlo.**
   Cada corrección se hace una sola vez y la siguiente sesión ya la sabe. Aprobarla te deja a ti decidir qué se vuelve regla, y ver el cambio exacto mantiene cortos los documentos.
2. **Cuando un documento y el código no coincidan, manda el código: trabaja con lo que dice el código y propón la corrección del documento.**
   El código es lo que se ejecuta. Un documento desactualizado se corrige, nunca se sigue.

## Cómo empezar

1. **Escribe el mapa.** Unas 20 líneas: qué es el proyecto, cómo se trabaja, a dónde ir según la tarea y qué nunca se hace. `create-agents-map` te entrevista y lo escribe a partir de [la plantilla](../skills/create-agents-map/assets/AGENTS.md).
2. **Agrega las dos reglas.** Ya vienen en la plantilla. `capture-lesson` aplica la primera cada vez que corriges al agente y `review-stale-docs` aplica la segunda en todo el proyecto.
3. **Un README en cada carpeta** a la que apunta el mapa: qué hay ahí y cómo se trabaja. [Plantilla](../skills/create-agents-map/assets/folder-README.md).
4. **Una skill para tu tarea más frecuente.** `turn-task-into-skill` la empaqueta como una [skill mínima](../skills/turn-task-into-skill/assets/minimal-skill.md), o como un [orquestador](../skills/turn-task-into-skill/assets/orchestrator-skill.md) con su [archivo de estado](../skills/turn-task-into-skill/assets/status.md) cuando el trabajo tiene varias etapas.
5. **Pasa a un script lo que es exacto.** `promote-rule-to-script` encuentra las reglas que un programa puede comprobar y propone el script o el hook. [`check-docs.py`](../skills/review-stale-docs/scripts/check-docs.py) es un ejemplo: comprueba que los enlaces y las rutas de tus documentos siguen existiendo.

## Las skills

| Skill | Qué hace |
|---|---|
| [`create-agents-map`](../skills/create-agents-map) | Te entrevista y escribe el `AGENTS.md` de la raíz con las dos reglas, y si quieres un README por carpeta |
| [`capture-lesson`](../skills/capture-lesson) | Convierte una corrección en un cambio exacto en el documento correcto, que se escribe cuando lo apruebas |
| [`turn-task-into-skill`](../skills/turn-task-into-skill) | Empaqueta una tarea repetida como skill mínima o como orquestador con archivo de estado |
| [`promote-rule-to-script`](../skills/promote-rule-to-script) | Encuentra las reglas exactas y repetidas y propone un script o un hook para cada una |
| [`review-stale-docs`](../skills/review-stale-docs) | Compara los documentos y las skills con el código, aplica «manda el código» y propone correcciones y retiros |

Las skills que necesitan algo de tu proyecto (un mapa, una herramienta) empiezan con una comprobación de prerrequisitos («Prerequisites») y te dicen qué falta antes de hacer nada.

Las skills están escritas en inglés y te responden en tu idioma.

## Plantillas

| Plantilla | Para qué |
|---|---|
| [`AGENTS.md`](../skills/create-agents-map/assets/AGENTS.md) | El mapa de la raíz, con las dos reglas |
| [`folder-README.md`](../skills/create-agents-map/assets/folder-README.md) | El README de una carpeta |
| [`minimal-skill.md`](../skills/turn-task-into-skill/assets/minimal-skill.md) | Una skill con un solo flujo; se guarda como `<nombre-de-la-skill>/SKILL.md` |
| [`orchestrator-skill.md`](../skills/turn-task-into-skill/assets/orchestrator-skill.md) | Una skill con tabla de rutas; se guarda como `<nombre-de-la-skill>/SKILL.md` |
| [`status.md`](../skills/turn-task-into-skill/assets/status.md) | El archivo de estado del trabajo en curso |

Las plantillas viven dentro de las skills que las usan, así cada skill funciona aunque la instales sola.

## Con cualquier agente

- Varios agentes leen el `AGENTS.md` de la raíz del repositorio. Si el tuyo lee otro nombre de archivo, crea ese archivo con una sola línea que apunte a `AGENTS.md`, para que las reglas vivan en un único lugar.
- Una skill es una carpeta con un archivo `SKILL.md`. Los agentes que soportan skills las cargan desde su carpeta de skills (por ejemplo `.agents/skills/` o `.claude/skills/`). Si tu agente no las soporta, el mapa igual puede apuntar a un `SKILL.md` como documento que se lee antes de la tarea.

## Qué evitar

- **Un archivo de instrucciones gigante.** El agente lo lee entero cada vez y sigue menos de lo que dice. El mapa va corto y el detalle vive junto a lo que describe.
- **Guardar cada instrucción.** «Por ahora» y «en este archivo» no son reglas. Solo se guarda lo que va a volver a importar.
- **Escribir lecciones sin aprobación.** Los documentos terminan diciendo lo que el agente supuso y no lo que tú decidiste.
- **Historia en los documentos.** Los documentos dicen cómo son las cosas hoy. Cuando una regla cambia, se reemplaza el texto viejo.
- **La misma regla en dos lugares.** Una de las copias se queda vieja. Guárdala en un solo sitio y enlázala desde los demás.
