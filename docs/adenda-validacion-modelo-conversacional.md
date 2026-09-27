# KOACH — Adenda de Validación y Modelo Conversacional
### Hallazgos de entrevistas + rediseño del núcleo de nutrición
> Complemento al Plan Maestro v6.0 — Mayo 2026

---

## PARTE 1 — HALLAZGOS DE VALIDACIÓN (3/15 entrevistas)

### 1.1 Resumen de resultados

| Métrica | Resultado |
|---------|-----------|
| Entrevistas realizadas | 3 de 15 |
| Usarían Koach | 3/3 (todos "sí") |
| Aceptan $149 founder en el momento | 3/3 |
| Precio real dicho espontáneamente | $190 / $120 / $100 |
| **Precio promedio real** | **$137 MXN** |
| Dolor #1 identificado | Alimentación (3/3) |
| Feature que más gustó | Ajuste automático de la comida (3/3) |
| Piden integración con wearables | 2/3 |
| Fuera del círculo cercano del entrevistador | 0/3 |

### 1.2 Hallazgos clave

**✅ Validado: el ajuste dinámico de comida es el producto**

Los tres entrevistados, sin coordinarse, señalaron como lo más atractivo la capacidad de ajustar la alimentación en tiempo real según lo que el usuario ya va a comer — no un plan rígido que hay que seguir.

**✅ Validado: la alimentación es el dolor dominante sobre el ejercicio**

Los tres ya entrenan con cierta regularidad (2-4 días/semana). Los tres identificaron la alimentación como su principal dificultad. Esto reordena la prioridad de desarrollo: nutrición conversacional > gamificación de ejercicio.

**⚠️ Alerta: el pricing objetivo puede estar sobrevalorado**

Precio dicho espontáneamente promedia $137 MXN, por debajo del precio founder de $149. El "sí" a $149 puede reflejar cortesía hacia el entrevistador (sesgo de amistad) más que disposición real de pago. Pendiente de confirmar con entrevistados fuera del círculo cercano.

**⚠️ Alerta: sesgo de muestra**

Las 3 entrevistas son del mismo círculo social (se conocen entre sí, perfil similar: hombres, entrenan regularmente). No representan la diversidad del mercado objetivo. **Pendiente crítico:** las siguientes 12 entrevistas deben salir deliberadamente de este círculo (ver plan de diversificación en documento de validación original).

**🔍 Hallazgo cualitativo importante — reinterpretación de "que me digan qué comer"**

Un entrevistado mencionó como algo que NO le ha funcionado en el pasado "que te digan estrictamente qué comer". Análisis: no es rechazo a la guía en sí, sino a la **rigidez** — planes que ignoran gustos, antojos y lo que el usuario ya tiene disponible. Esto llevó al rediseño documentado en la Parte 2.

**📌 Pendiente sin resolver:** la pregunta "¿qué NO te gusta de la idea?" no ha capturado objeciones reales — las respuestas obtenidas fueron peticiones de features (wearables, básculas), no objeciones. Ajustar el guion para las siguientes entrevistas, insistiendo con: *"¿qué te haría NO usarlo?"* o *"¿qué te daría flojera de esto?"*

### 1.3 Ajustes al plan derivados de estos hallazgos

| Área | Cambio |
|------|--------|
| Posicionamiento | De "coach de salud integral" a "el coach que ajusta tu comida a tu vida real" |
| Prioridad de desarrollo | Nutrición conversacional adelanta a gamificación de ejercicio |
| Pricing | Mantener $149 founder pero monitorear de cerca; considerar tier de entrada más bajo si el patrón se confirma en las siguientes 12 entrevistas |
| Modelo de planes | Rediseño completo — ver Parte 2 |
| Wearables | Evaluar como señal, no como decisión — confirmar con más entrevistas antes de comprometer roadmap |

---

## PARTE 2 — MODELO CONVERSACIONAL DE ALIMENTACIÓN (rediseño)

### 2.1 Principio rector

> Koach nunca prescribe. Koach negocia.

El modelo anterior (plan semanal fijo generado el domingo, el usuario lo sigue) se reemplaza por un **modelo de negociación diaria** donde el usuario propone o Koach sugiere desde sus gustos conocidos, y el ajuste ocurre en tiempo real.

### 2.2 Los dos flujos

**Flujo A — Koach propone primero**

Cuando el usuario no ha dicho qué quiere comer, Koach sugiere basado en: alacena disponible + gustos conocidos + macros restantes del día.

```
Koach: Buenas tardes 🍽️ Para la comida vi que tienes pollo,
calabacitas y arroz. Sé que te gusta con chile, así que se
me ocurre pollo a la mexicana con calabacitas.

Te falta jitomate y cebolla — como $25 en la tiendita.

¿Te late o quieres otra opción?

Usuario: otra

Koach: Va. Opción 2: arroz frito con pollo y verduras.
Con lo que ya tienes, sin comprar nada. ~480 kcal.

Opción 3: tacos de pollo con calabacita. Necesitas tortillas.

¿Alguna te late?
```

**Flujo B — El usuario propone, Koach acomoda**

Cuando el usuario ya sabe o se le antoja algo específico, Koach nunca lo bloquea — lo ajusta.

```
Usuario: se me antojan unas quesadillas

Koach: ¡Va! Con lo que llevas hoy te alcanzan bien 🫓
3 quesadillas de queso con champiñones ≈ 520 kcal.
Si les pones nopal encima te llenan más y sumas fibra.

¿Te las echas así o le movemos algo?
```

**Flujo C — Comida "fuera de la guía" (antojo, salida a comer)**

Nunca se trata como falla. Se acomoda y se sigue adelante.

```
Usuario: voy a ir por unos tacos al pastor

Koach: Va, disfrútalos 🌮
Te sugiero 4 y agua fresca sin azúcar. Con eso te quedas
bien para hoy.

Si te echas 6, no pasa nada — mañana bajamos un poco los
carbos y seguimos. Tú decides.
```

### 2.3 Reglas de diseño del modelo

**Regla 1 — Siempre 3 opciones cuando Koach propone**
Una sola sugerencia se siente como orden. Tres se sienten como menú. Nunca menos de 2, nunca más de 3 (sobrecarga de decisión).

**Regla 2 — Brecha mínima de compra**
Orden de prioridad al sugerir:
```
1º Solo con lo que hay en alacena           → prioridad máxima
2º Falta 1-2 ingredientes baratos           → aceptable, se menciona costo aprox.
3º Falta 3+ ingredientes o algo caro        → solo si el usuario lo pide
```

**Regla 3 — Nunca prohibir, siempre acomodar**
Ningún alimento está vetado salvo alergia real. Ante un "exceso", Koach reconoce, ajusta el resto del día o de la semana, y sigue sin culpa ni regaño.

**Regla 4 — Aprendizaje por rechazo**
Cada "otra" o "no me gusta" se registra como señal. Tres rechazos al mismo tipo de preparación o ingrediente → se marca como no preferido automáticamente, sin que el usuario tenga que declararlo explícitamente.

### 2.4 Perfil de gustos ampliado (nuevo modelo de datos)

El campo `preferencias_alimentos` existente (definido en `docs/plan-maestro.md` sección 14) se queda corto para este modelo. Se amplía con dos tablas nuevas — **agregar estas junto con las de `plan-maestro.md`, no en su lugar**:

```sql
CREATE TABLE perfil_gustos (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    estilos_preferidos JSONB,       -- ["picante", "guisado", "antojito"]
    estilos_evitados JSONB,         -- ["hervido", "al_vapor"]
    proteinas_favoritas JSONB,      -- ["pollo", "huevo", "res"]
    proteinas_evitadas JSONB,       -- ["pescado", "higado"]
    verduras_aceptadas JSONB,
    verduras_rechazadas JSONB,
    metodos_preferidos JSONB,       -- ["asado", "guisado"]
    metodos_evitados JSONB,
    tiempo_cocina_min INT,          -- tolerancia típica
    complejidad_tolerada ENUM('baja', 'media', 'alta'),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE rechazos_sugerencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    sugerencia_id UUID,
    ingrediente_o_metodo VARCHAR(100),
    veces_rechazado INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Cómo se llena:** nunca con un formulario. Se infiere de las correcciones y rechazos naturales durante el uso — cada "otra opción" es una fila potencial en `rechazos_sugerencias`; al llegar a 3 rechazos del mismo patrón, se promueve a `perfil_gustos.estilos_evitados`.

### 2.5 Impacto en el System Prompt

Se agrega bloque nuevo al system prompt maestro (vive en `app/ai/prompts/`, nunca hardcodeado en Python — ver ADR-003 en `docs/plan-desarrollo-sdd.md`):

```
MODELO DE SUGERENCIA DE COMIDAS — REGLAS OBLIGATORIAS:

1. NUNCA presentes un plan como orden fija. Siempre como propuesta.
2. Si el usuario propone algo, tu trabajo es ACOMODARLO, no bloquearlo.
3. Da máximo 3 opciones cuando tú propones.
4. Prioriza siempre lo que ya está en su alacena.
5. Si falta algo, menciona qué y aproxima el costo.
6. Nunca uses tono de regaño ante excesos o antojos. Ajusta y sigue.
7. Si el usuario rechaza una opción, ofrece otra sin preguntar por qué
   (a menos que el patrón de rechazo ya sea claro).
```

Nota (ADR-007, arquitectura agéntica): este bloque informa el comportamiento de la tool `sugerir_comida` del catálogo de US-159, no un router de texto libre. La tool ejecuta esta lógica de negociación; el bucle agéntico (US-160) decide cuándo invocarla.

---

## PARTE 3 — REGISTRO POR FOTO (diseño técnico)

### 3.1 Principio rector

> Precisión suficiente para la tendencia, no precisión de laboratorio. Consistencia y baja fricción valen más que exactitud.

### 3.2 Realidad de precisión de los modelos de visión (referencia)

| Tarea | Precisión realista |
|-------|---------------------|
| Identificar qué platillo es | 80-90% |
| Identificar ingredientes visibles | 70-85% |
| Estimar la porción | 40-60% ⚠️ |
| Detectar grasas/azúcares ocultos | 30-50% ⚠️ |
| Comida mexicana en guisado | 50-70% ⚠️ |

**Implicación de diseño:** el sistema no puede confiar ciegamente en la estimación visual. Requiere un paso de confirmación selectivo.

### 3.3 Pipeline de 4 pasos

```
1. IDENTIFICAR
   Claude Vision analiza la foto → lista de componentes + confianza por ítem

2. ESTIMAR
   Cada componente se busca en alimentos_mexicanos
   Se usan porciones estándar como ancla
   Se marca nivel de certeza de la porción

3. CONFIRMAR (selectivo, no exhaustivo)
   Solo se pregunta donde la incertidumbre es alta
   Nunca más de 1 pregunta por foto

4. APRENDER
   La corrección del usuario se guarda
   Sirve para calibrar futuras estimaciones de platos similares
```

### 3.4 Ejemplo de confirmación bien diseñada

**❌ Mal — interrogatorio:**
> ¿Cuántos gramos de arroz? ¿Qué aceite usaste? ¿Era carne magra?

**✅ Bien — una sola pregunta, la de mayor impacto:**
> Veo pollo con arroz y ensalada 🍽️ Calculo ~550 kcal.
> Solo una cosa: ¿el arroz era como media taza o un plato lleno?

**✅ Alternativa con botones:**
```
Porción del arroz:
[🥄 Poquito]  [🍚 Normal]  [🍛 Bastante]
```

### 3.5 Resolución del problema de escala

**Opción A — Objeto de referencia**
Sugerir incluir la mano o un tenedor en la foto para dar escala automática al modelo de visión.

**Opción B — Aprendizaje de la vajilla del usuario (preferida a mediano plazo)**
Las primeras 10-15 fotos, Koach pregunta porción activamente. Después, ya conoce el tamaño típico de los platos del usuario y reduce las preguntas.

```
Koach: "Ya voy conociendo tus platos, así que ya casi no
te voy a tener que preguntar 😄"
```

### 3.6 Comunicación de expectativas al usuario

Mensaje explícito en el onboarding o primera vez que se usa registro por foto:

```
"Mis cálculos por foto son aproximados, no exactos. Lo que
más importa es la tendencia en el tiempo, no el número
perfecto de cada comida."
```

Esto reduce fricción de confianza y evita frustración por imprecisión normal del sistema.

### 3.7 Modelo de datos

```sql
ALTER TABLE registros_comida ADD COLUMN foto_url VARCHAR;
ALTER TABLE registros_comida ADD COLUMN foto_confianza_general DECIMAL(3,2);
ALTER TABLE registros_comida ADD COLUMN porcion_confirmada_usuario BOOLEAN DEFAULT FALSE;

CREATE TABLE calibracion_porciones_usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    tipo_platillo VARCHAR(100),
    porcion_tipica_g INT,
    veces_confirmado INT DEFAULT 1,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.8 Consideraciones de costo

Cada foto analizada con Claude Vision tiene costo por token de imagen. Estimado: 30 usuarios × 3 fotos/día ≈ 2,700 imágenes/mes.

**Decisión de producto:** registro por foto disponible en plan Coach o superior, no en Esencial. Límite razonable de fotos/día para evitar abuso (ver US-134 Circuit Breaker de costos, en `docs/analisis-brechas.md`).

### 3.9 Fase de implementación

| Fase | Alcance |
|------|---------|
| MVP (Fase 1) | Solo registro por texto y voz — **sin foto** |
| Fase 2 | Registro por foto con confirmación siempre activa |
| Fase 3 | Aprendizaje de porciones típicas del usuario (`calibracion_porciones_usuario`) |
| Fase 4 | Estimación autónoma con alta confianza, confirmación solo en casos ambiguos |

**Justificación de no incluir en MVP:** es la funcionalidad más costosa de construir bien (requiere pipeline de 4 pasos, calibración, manejo de incertidumbre). Se prioriza primero validar el modelo conversacional de texto, que ya fue validado como el gancho principal en las entrevistas.

---

## PARTE 4 — USER STORIES DE ESTE DOCUMENTO (ya reflejadas en `docs/plan-desarrollo-sdd.md` y `docs/analisis-brechas.md`)

### EP-09 (ampliada) — Alacena y Sugerencias Conversacionales

**US-145: Modelo de perfil de gustos por capas** (🔴 Alta, 4 hrs)
Implementar tabla `perfil_gustos` y lógica de inferencia desde correcciones.

**US-146: Motor de sugerencia con 3 opciones** (🔴 Alta, 5 hrs)
Reemplaza la generación de plan semanal fijo por sugerencia conversacional diaria con brecha mínima de compra.

**US-147: Flujo "usuario propone, Koach acomoda"** (🔴 Alta, 4 hrs)
Detección de intención de comida propuesta por el usuario y ajuste automático de macros restantes del día.

**US-148: Registro de rechazos y promoción a preferencia** (🟠 Media, 3 hrs)
Tabla `rechazos_sugerencias` con lógica de promoción automática a `perfil_gustos` tras 3 rechazos del mismo patrón.

### EP-32 (nueva) — Registro por Foto

**US-149: Pipeline de identificación con Claude Vision** (🟡 Fase 2, 5 hrs)
**US-150: Motor de confirmación selectiva** (🟡 Fase 2, 4 hrs)
**US-151: Calibración de porciones por usuario** (🟢 Fase 3, 4 hrs)
**US-152: Límites de costo para registro por foto** (🟡 Fase 2, 2 hrs)

> Nota: estas US están mencionadas en `docs/00-indice-maestro.md` como "pendientes de agregar formalmente a la numeración" de `plan-desarrollo-sdd.md`. Al implementarlas, usar las specs de este documento (Partes 2 y 3) como la definición completa — no reinventar el diseño del pipeline de foto ni el modelo conversacional.

---

## PARTE 5 — PENDIENTES ACTUALIZADOS

Se agregan estos pendientes al registro general (`docs/adenda-legal-pendientes.md`):

| # | Pendiente | Prioridad |
|---|-----------|-----------|
| P-17 | Completar las 12 entrevistas restantes, priorizando fuera del círculo cercano | 🔴 |
| P-18 | Ajustar guion de entrevista: insistir en "¿qué te haría NO usarlo?" | 🔴 |
| P-19 | Confirmar o descartar hipótesis de pricing $149 con muestra diversa | 🔴 |
| P-20 | Decidir sobre integración de wearables según señal de próximas entrevistas | 🟡 |
| P-21 | Escribir y probar los prompts reales del modelo conversacional (simulación manual) | 🟠 |

---

*Adenda de Validación y Modelo Conversacional v1.0*
*Koach — Mayo 2026*
