> ## ⚠️ NOTA DE VIGENCIA (leer antes que el resto del documento)
>
> Este es el Plan Maestro original (v6.0, mayo 2026) — la visión y el esquema de
> base de datos completo del producto. Sigue siendo la **fuente de verdad para el
> modelo de datos (sección 14)** y para la visión/esencia general del producto
> (secciones 1-10). **No lo redefinas ni rediseñes tablas ya definidas aquí.**
>
> Sin embargo, varias decisiones puntuales de este documento quedaron
> **corregidas por documentos posteriores** — si hay conflicto, gana el documento
> más reciente:
>
> | Tema en este documento | Estado actual | Dónde está la corrección |
> |---|---|---|
> | Plan nutricional como "plan fijo semanal" (Módulo 2.3) | Reemplazado por modelo conversacional de negociación diaria | `docs/adenda-legal-pendientes.md` y notas de `docs/plan-desarrollo-sdd.md` |
> | Precio $299 MXN plan Coach (sección 29) | En duda — entrevistas reales sugieren ~$137-149 MXN | No resuelto aún, no usar como dato duro |
> | "Nutriólogo consultor" como mejora en mes 6 (sección 2.4) | Ahora es **requisito antes de cobrar**, no opcional | `docs/adenda-legal-pendientes.md`, Parte 1 |
> | Lenguaje "plan nutricional", "dieta", "prescribimos" | Evitar — riesgo de ejercicio profesional no autorizado | `docs/adenda-legal-pendientes.md`, sección 1.6 |
> | Costo de WhatsApp Cloud API asumido en $0 (sección 30) | Corregido — costo real ~$1.20-2.16 USD/usuario/mes | Ver notas de costos en `docs/analisis-brechas.md` |
> | Router de IA "clasificar y rutear" (sección 11.2) | **Reemplazado por arquitectura agéntica con tool-use nativo (ADR-007)** | `docs/plan-desarrollo-sdd.md`, ADR-007 y EP-06 bis |
> | Claude Sonnet 4.6 / modelos nombrados específicos | Los nombres de modelo cambian — usar la abstracción de `docs/plan-desarrollo-sdd.md` (`LLMProvider`), no hardcodear versiones | `docs/plan-desarrollo-sdd.md`, sección 3 |
> | US-134 a US-144, ciclo de vida de cuentas, EP-31 | No estaban en este documento — se agregaron después | `docs/analisis-brechas.md`, `docs/ciclo-vida-usuario.md` |
>
> **Lo que SÍ sigue vigente tal cual:** el esquema completo de base de datos
> (sección 14), la visión y misión (sección 1), la arquitectura de dos
> superficies WhatsApp+App (sección 12), el stack tecnológico (sección 13,
> aunque ver la nota de ADR-007 sobre el router), las bases científicas de
> nutrición (sección 17), y la estructura del equipo (sección 2).

---

# KOACH — Plan Maestro v6.0 (Definitivo)
### Coach de salud proactivo para mexicanos
> Documento integral de producto, empresa, arquitectura, desarrollo, marketing y operación
> Versión final consolidada — Mayo 2026
> Cofundadores: Jaziel Anguiano (CTO/Producto) + Maira Anguiano (CEO/Marketing)

---

## ÍNDICE COMPLETO

### Parte I — Estrategia y Producto
1. Visión, misión y propuesta de valor
2. Estructura del equipo y empresa
3. Propiedad intelectual y marca
4. Funcionalidades completas del producto
5. Personalización profunda por usuario
6. Adaptación por rango de edad
7. Educación en salud como diferenciador
8. Sistema de retención a largo plazo
9. Beneficios para usuarios founders
10. Políticas comerciales y de suscripción

### Parte II — Arquitectura Técnica
11. Estrategia de IA multi-modelo
12. Arquitectura de dos superficies (WhatsApp + App)
13. Stack tecnológico completo
14. Base de datos detallada
15. Reportes PDF y Excel
16. Sistema de ejercicios
17. Bases científicas de las dietas

### Parte III — Seguridad y Compliance
18. WhatsApp Cloud API — reglas críticas
19. LFPDPPP 2025 — Cumplimiento legal
20. Seguridad técnica y datos sensibles
21. Protección del agente IA
22. Protocolos de emergencia
23. Botón de emergencia y crisis

### Parte IV — Marketing y Crecimiento
24. Estrategia de marketing
25. Página web robusta
26. Rol de Maira y plan editorial
27. Sistema de retroalimentación
28. Comunicación de funcionalidades

### Parte V — Modelo de Negocio
29. Pricing y planes
30. Proyección financiera
31. Métricas de éxito
32. Riesgos y mitigaciones

### Parte VI — Ejecución
33. Metodología SDD
34. Plan de desarrollo por fases
35. Roadmap futuro (Fase 4+)

---

# PARTE I — ESTRATEGIA Y PRODUCTO

## 1. VISIÓN, MISIÓN Y PROPUESTA DE VALOR

### 1.1 Nombre y posicionamiento

**Nombre:** Koach
**Tagline principal:** *"Tu coach de salud. Siempre contigo."*
**Tagline alternativo:** *"El coach que te busca a ti."*

### 1.2 Misión

Democratizar el acceso a un coach personal de salud para mexicanos que no tienen tiempo, dinero o disciplina para apps complejas, usando WhatsApp como canal principal y tecnología que aprende de cada usuario.

### 1.3 Visión

En 5 años: Ser la app de salud preventiva más usada por mexicanos de clase media, con 50,000+ usuarios activos y una comunidad de personas más sanas físicamente, mentalmente y educacionalmente.

### 1.4 Propuesta de valor única

> "El único coach de salud que te busca a ti, con contexto mexicano real, en el WhatsApp que ya usas, a precio de una suscripción de streaming."

### 1.5 Diferenciadores únicos vs competencia

| Diferenciador | Por qué nadie más lo tiene |
|---------------|---------------------------|
| Proactividad en WhatsApp | Apps gringas no entienden el ecosistema MX |
| Contexto cultural mexicano | Imposible replicar desde fuera |
| Conocimiento acumulado del usuario | Crece con tiempo, irreplicable |
| Educación en salud integrada | Apps tradicionales solo trackean |
| Multi-IA según tarea | Optimización de costo/calidad |
| Equipo local en Colima | Soporte y comprensión cultural real |

---

## 2. ESTRUCTURA DEL EQUIPO Y EMPRESA

### 2.1 Cofundadores

**Maira Anguiano — Cofundadora y CEO**
- Titular legal de la empresa
- Encargada de marketing, branding y crecimiento
- Construcción de presencia en redes sociales
- Gestión de comunidad y atención pre-venta
- Visión de marca y experiencia de usuario
- Reuniones con partners (gimnasios, alianzas)

**Jaziel Anguiano — Cofundador y CTO**
- Encargado de producto y tecnología
- Desarrollo completo del backend y app
- Decisiones técnicas y arquitectónicas
- Gestión legal/fiscal interna (es contador)
- Soporte técnico a usuarios

### 2.2 Estructura legal evolutiva

**Fase inicial (Mes 1-12):**
Maira se da de alta en SAT con régimen RESICO PF + Actividad Empresarial.

- Sin costo de constitución
- Tasa ISR baja:
  - Hasta $25k MXN/mes: **1%**
  - Hasta $50k MXN/mes: **1.1%**
  - Hasta $83k MXN/mes: **1.5%**
- Facturación CFDI desde día 1
- Contabilidad llevada internamente por Jaziel
- IVA 16% trasladado al usuario

**Migración a SAS (Mes 12+ si aplica):**
Cuando los ingresos lo justifiquen, constituyen Koach Technologies S.A.S. de C.V. con ambos como socios al 50/50.

### 2.3 Acuerdo entre cofundadores

Aunque sean esposos, conviene documentar:
- Reparto de ingresos (sugerencia: 100% reinvertido los primeros 6 meses, luego reparto según acuerdo)
- División de áreas de decisión
- Política de migración a SAS y reparto accionario
- Plan ante separación o disputa (improbable pero documentado)

Documento simple en Notion firmado por ambos. No requiere notario inicialmente.

### 2.4 Crecimiento del equipo (Roadmap)

| Mes | Rol nuevo | Cuándo se justifica |
|-----|-----------|---------------------|
| 6-9 | Nutriólogo registrado (consultor) | Para validación profesional |
| 9-12 | Editor de contenido (freelance) | Cuando blog/redes crezcan |
| 12+ | Desarrollador junior | Cuando Jaziel sea cuello de botella |
| 18+ | Customer success | A los 200+ usuarios |

---

## 3. PROPIEDAD INTELECTUAL Y MARCA

### 3.1 Registro de marca ante el IMPI

**Costos:**
- ~$2,851 MXN por clase (Marca en Línea con 10% desc.)
- Tiempo: 4-6 meses aprobación

**Clases recomendadas:**
- **Clase 42** — Software/SaaS (prioritaria — registrar primera)
- **Clase 44** — Salud y bienestar (segunda)
- **Clase 41** — Educación, coaching (tercera)

**Total para 3 clases:** ~$8,500 MXN

**Cuándo registrar:** Mes 3-4 cuando ingresos lo justifiquen. Empezar con Clase 42 sola y agregar después.

### 3.2 Búsqueda fonética previa

Antes de pagar el registro:
- Buscador en marcanet.impi.gob.mx (gratis)
- Si suena igual a marca existente → riesgo de rechazo
- Si está limpio → proceder con registro

### 3.3 Dominios

Registrar en semana 1:
- **koach.mx** — principal (~$350 MXN/año)
- **koach.app** — alternativo (~$400 MXN/año)
- **koach.health** — opcional (~$500 MXN/año)

### 3.4 Redes sociales

Reservar usernames en semana 1:
- Instagram: @koach.app
- TikTok: @koach.app
- Facebook: /koach.app
- X (Twitter): @koachapp
- LinkedIn: /company/koach

### 3.5 Identidad visual

**Paleta de colores:**
- Verde principal: salud, frescura — #10B981
- Azul oscuro: confianza, profesional — #1E293B
- Acento cálido: energía — #F59E0B
- Fondo claro: limpieza — #FAFAFA

**Tipografía:**
- Display: Geist Sans o similar moderno
- Body: Inter o Manrope

**Logo:**
- Simple, memorable
- Funciona en pequeño (favicon, app icon)
- Diseño contratado en Workana/Fiverr: $800-2,500 MXN

---

## 4. FUNCIONALIDADES COMPLETAS DEL PRODUCTO

### MÓDULO 1 — Agente Proactivo (Core diferenciador)

**Agenda diaria tipo personalizable:**

| Hora | Mensaje | Canal |
|------|---------|-------|
| 7:00 am | Buenos días + desayuno + agua | WhatsApp |
| 9:30 am | Checkin desayuno | WhatsApp |
| 11:00 am | Recordatorio colación AM | WhatsApp |
| 1:30 pm | Sugerencia comida del día | WhatsApp |
| 3:30 pm | Hidratación | WhatsApp |
| 4:00 pm | Colación PM | WhatsApp |
| 6:30 pm | Checkin ejercicio | WhatsApp |
| 8:30 pm | Checkin cena | WhatsApp |
| 9:30 pm | Resumen del día + racha | WhatsApp + Push |
| 10:30 pm | Recordatorio de dormir | WhatsApp (opcional) |

**Comportamiento inteligente:**
- Aprende patrones del usuario y ajusta automáticamente
- Si no responde 2 checkins → ajusta tono y frecuencia
- Anticipa eventos recurrentes
- Modo silencio configurable (vacaciones, descansos)

**Tonos adaptativos:**
- 🪖 Drill Sergeant — directo, exigente
- 🧠 Coach — motivador, empático
- 😄 Amigo — casual, humor mexicano
- 🤵 Formal — para usuarios mayores 40+

---

### MÓDULO 2 — Nutrición Inteligente

**2.1 Plan Nutricional Personalizado**
Calculado con bases científicas (ver Sección 17):
- TDEE con Mifflin-St Jeor
- Macros según meta (proteína 1.6-2.2g/kg, grasas 20-30%, carbs el resto)
- 5 tiempos de comida configurables
- Adaptable a restricciones declaradas

**2.2 Registro de Alacena**
- Por WhatsApp en lenguaje natural
- Estructura guardada en DB
- Actualización fácil cualquier momento
- Visible en app

**2.3 Plan Semanal de Comidas** *(ver nota de vigencia: reemplazado por modelo conversacional)*
- Generado cada domingo automáticamente
- Basado en plan + alacena + gustos + presupuesto
- Adaptado a actividades de la semana (eventos, viajes)
- PDF descargable disponible

**2.4 Sugerencias Alternativas**
- "No tengo X, ¿con qué lo cambio?"
- Mantiene macros equivalentes
- Considera alimentos accesibles en México

**2.5 Modo "Comí Fuera"**
- Apps de entrega (Didi, Uber Eats, Rappi)
- Taquería/fonda con base de estimados
- Restaurant/aeropuerto/viaje
- Ajuste automático del resto del día

**2.6 Lista de Compras Automática**
- Compara plan semanal vs alacena
- Agrupada por categoría
- Enviada por WhatsApp + PDF
- Editable antes de imprimir/ir al súper

**2.7 Base de Alimentos Mexicanos**
- USDA + extensión local con +500 alimentos
- Incluye platillos típicos con estimados
- Expandida conforme usuarios reportan platillos nuevos

**2.8 Modo "Cocino para familia"**
- Recetas escalables para 2-6 personas
- Adaptaciones por edad (niños toleran menos picante, etc.)
- Sugerencias balanceadas que toda la familia disfruta

---

### MÓDULO 3 — Entrenamiento Adaptativo

**3.1 Plan de Ejercicio Personalizado**
- Configurado en onboarding: objetivo, tiempo, equipamiento
- Rutina semanal con progresión automática cada 2 semanas
- PDF descargable con descripciones y videos

**3.2 Pivote en Tiempo Real**
- Aparato ocupado → alternativa mismo músculo
- Solo 15 min → rutina exprés
- En hotel → rutina sin equipo
- Dolor en X → rutina adaptada

**3.3 Modo Gym Avanzado**

**3.3.1 Seguimiento de cargas:**
> *"Hoy hice sentadilla con 80kg — 4x10"*
> Koach guarda. Próxima sesión: *"La semana pasada 80kg, ¿vamos por 82.5?"*

**3.3.2 Buscar gym cuando viajas:**
> *"Estoy en Guadalajara"*
> Koach: *"Te ubico opciones cercanas 📍"*

Google Places API integrada.

**3.3.3 Doble plan gym/casa:**
Si varía, Koach pregunta cada día qué aplica.

**3.4 Modo "Tengo X minutos"**
Rutina optimizada para el tiempo disponible.

**3.5 Registro de Entrenamientos**
- Botones rápidos: ✅ / ⚡ / ❌
- Lenguaje natural
- Audios de voz

**3.6 Biblioteca de Ejercicios** ⭐ Crítico para usuarios nuevos

Cada ejercicio incluye:
- Nombre principal + alternativos mexicanos
- Video corto 15-30 seg (YouTube en MVP, propio en Fase 2)
- Foto del aparato si aplica
- Descripción simple
- Músculo principal trabajado
- Errores comunes a evitar
- Alternativas si no hay aparato

Sistema de detección: cuando usuario dice "no sé qué es X" → Koach manda video automáticamente.

---

### MÓDULO 4 — Hidratación Inteligente

- Meta diaria por peso y actividad
- Recordatorios basados en patrones del usuario, no genéricos
- Registro rápido (botón o texto)
- Contador visible en app y resumen nocturno
- Ajuste por clima (verano en Colima = más agua)

---

### MÓDULO 5 — Sueño y Descanso ⭐ Nuevo módulo importante

**5.1 Tracking de sueño**
- Hora de dormir registrada por usuario
- Hora de despertar
- Calidad subjetiva (1-5)
- Patrones detectados

**5.2 Recordatorios de sueño**
> *"Son las 10:30 pm — mañana hay rutina temprano 😴 30 min para dormir te ayudaría"*

**5.3 Higiene del sueño (educativo)**
- Tips integrados al contenido educativo
- Cafeína después de cierta hora
- Pantallas antes de dormir
- Rutina de descenso

**5.4 Integración con plan**
- Mal sueño → ajustar intensidad de ejercicio
- Buen sueño → puede entrenar más duro
- Adaptación automática

**5.5 Alarmas inteligentes**

**Para usuarios solo de WhatsApp:**
- Mensaje a hora exacta como recordatorio sonoro
- Sugerir configurar alarma del celular
- Detectar cuándo se levanta naturalmente

**Para usuarios con app instalada (Fase 3):**
- Alarma nativa con push notification
- Modo "despierta para ejercitar" — audio motivacional
- Snooze inteligente que escala motivación

**5.6 Integración Google Calendar (Fase 4)**
- Conectar calendar (OAuth)
- Ver eventos para ajustar sugerencias
- Agendar rutinas automáticamente
- Bloqueos de tiempo protegidos

---

### MÓDULO 6 — Educación en Salud ⭐ Diferenciador estratégico

**6.1 Tips diarios contextualizados**

Koach manda 1 tip por día integrado a la conversación:
> *"Dato útil ☝️ Las leguminosas como frijoles tienen más proteína que muchas carnes — y son más baratas."*

Características:
- Educativos, no médicos
- Basados en consenso científico (OMS, AMENAC)
- Contexto cultural
- Cortos para WhatsApp

**6.2 Biblioteca "Aprende" en la app**

Sección con contenido educativo:
- Macronutrientes explicados
- Cómo leer etiquetas
- Mitos comunes desmentidos
- Tipos de ejercicio
- Importancia del sueño
- Estrés y cortisol
- Hidratación científica

Cada artículo 3-5 min de lectura. Contenido propio basado en fuentes confiables.

**6.3 "Pregúntale a Koach"**

> *"¿Es malo el café?"*
> Koach responde con información balanceada, citando consenso, sin diagnosticar.

**6.4 Reglas de oro educativas (legal)**

Koach SIEMPRE:
1. NO diagnostica
2. NO prescribe medicamentos
3. NO promete curas
4. Disclaimer en cada respuesta médica
5. Si menciona condición → recomienda profesional
6. Cita fuentes confiables

---

### MÓDULO 7 — Avances y Progreso

**7.1 Peso (semanal):**
Cada lunes: pregunta peso, muestra tendencia.

**7.2 Cumplimiento diario:**
Automático en resumen nocturno.

**7.3 Medidas corporales (mensual, opcional):**
Cintura, cadera, pecho, brazo, pierna.

**7.4 Fotos de progreso (mensual, opcional):**
Recordatorio para tomarse foto cada 4 semanas.

**7.5 Score de Salud (en app):**
Métrica compuesta: cumplimiento + hidratación + ejercicio + nutrición.

**7.6 Reportes**

**PDF generados automáticamente:**

**Reporte 1 — Plan Nutricional Inicial**
Al completar onboarding. Incluye TDEE explicado, macros, distribución, ejemplos.

**Reporte 2 — Plan de Entrenamiento Inicial**
Rutina semanal con descripciones y videos.

**Reporte 3 — Reporte Semanal**
Cada domingo: cumplimiento, macros, ejercicios, peso, racha, logros.

**Reporte 4 — Reporte Mensual**
Comparativa vs mes anterior, tendencias, evolución, motivacional.

**Reporte 5 — Lista de Compras Semanal**
Estructurada por categoría.

**Reporte 6 — Reporte Anual** ⭐ Diferenciador
Al cumplir 1 año: año completo visual, comparativa fotos, total ejercicios, racha máxima, premio simbólico.

**Excel opcional:**
Para usuarios que quieran analizar datos crudos:
- Historial completo de comidas
- Historial de ejercicios
- Pesos y medidas
- Para usuarios "data-driven"

---

### MÓDULO 8 — Gamificación

**Rachas:**
- Días consecutivos con checkin completo
- Notificaciones especiales: 3, 7, 14, 30, 60, 90, 180, 365 días

**Logros desbloqueables:**
- Primera semana
- Primer plan generado
- 30 días hidratación
- Meta de peso alcanzada
- Rachas progresivas

**Reporte dominical motivacional**

**Score de salud visible**

---

### MÓDULO 9 — Onboarding Progresivo

**Día 1 (5 min):** Solo lo esencial — nombre, edad, peso, talla, género, meta, alergias.
Koach genera plan del día YA.

**Días 2-7:** Una pregunta diaria, conversacional:
- Día 2: Horarios reales de tu día
- Día 3: Alacena actual
- Día 4: Familia y presupuesto
- Día 5: Motivación profunda
- Día 6: PAR-Q + lesiones + ciclo menstrual si aplica
- Día 7: Primer reporte semanal + ajustes

---

### MÓDULO 10 — Personalización Profunda

**10.1 Información que Koach acumula:**
- Datos básicos (peso, talla, edad)
- Plan nutricional y de ejercicio
- Alacena disponible
- Horarios
- Tono preferido
- Restricciones (alergias, condiciones)
- **Motivación personal (su "por qué")**
- **Contexto laboral y familiar**
- **Lesiones permanentes**
- **Ciclo menstrual (opcional)**
- **Presupuesto semanal**
- **Preferencias alimentos (gusta/no gusta)**
- **Patrones aprendidos**
- Historial 30 días

**10.2 Centro "Mi Koach" en la app:**
El usuario VE y EDITA todo lo que Koach sabe de él.

**10.3 Detección sutil de información:**
Preguntas integradas en conversación, no interrogatorio:
- Nivel socioeconómico (frecuencia de compras)
- Contexto familiar
- Nivel de actividad real
- Motivaciones profundas
- Barreras anteriores

Reglas:
- Una pregunta a la vez
- Espaciadas en tiempo
- Vinculadas a contexto
- Opcionales explícitas
- Beneficio visible
- Sin temas tabú

**10.4 El moat: conocimiento acumulado**
```
Mes 1 → Sabe tu meta básica
Mes 2 → Conoce gustos y patrones
Mes 3 → Sabe por qué empezaste
Mes 6 → Te conoce mejor que cualquier app
Mes 12 → Es irreemplazable
```

---

## 5. PERSONALIZACIÓN PROFUNDA POR USUARIO

*(Detallado en Sección 4 — Módulo 10)*

---

## 6. ADAPTACIÓN POR RANGO DE EDAD

### 6.1 Usuarios 18-39 años — Configuración estándar

Es el usuario por defecto. Plan, tono y funcionalidades como descritas.

### 6.2 Usuarios 40-70 años ⭐ Adaptación importante

**Características:**
- Saben usar WhatsApp (ventaja)
- Pueden tener vista cansada
- Más lentos para responder
- Probabilidad alta de condiciones médicas
- Motivación: salud preventiva > estética

**Adaptaciones automáticas (detectadas por edad en onboarding):**

**Lenguaje:**
- Más formal por default
- Sin slang ni emojis excesivos
- Frases más cortas y claras
- Opción "Don/Doña" si lo prefieren

**Plan nutricional:**
- Énfasis en alimentos antiinflamatorios
- Control de sodio si hipertensión declarada
- Control de azúcares si diabetes
- Mayor proteína (prevención sarcopenia)
- Considerar masticación y digestión

**Plan de ejercicio:**
- Énfasis en flexibilidad y movilidad
- Fuerza moderada (crítico a esta edad)
- Equilibrio (previene caídas)
- Cardio bajo impacto
- Calentamiento más largo
- Recuperación más larga

**PAR-Q exhaustivo:**
- Preguntas específicas sobre presión arterial
- Historial cardíaco
- Medicamentos actuales
- Marcapasos → derivación médica obligatoria

**Funcionalidades específicas:**
- Texto ligeramente más largo y descriptivo
- Recordatorios de medicamentos (opcional)
- Recordatorios de chequeos rutinarios
- "Modo paciente" — espera más tiempo de respuesta

### 6.3 Menores de 18 años — Política de exclusión

**Decisión:** NO aceptar menores en MVP.

**Razones:**
1. LFPDPPP — Consentimiento parental verificable requerido
2. Riesgo ético — Vulnerabilidad a trastornos alimentarios
3. WhatsApp/Meta — Términos requieren 13+ años
4. Recursos — Atención especializada que no podemos ofrecer

**Implementación:**

En onboarding:
> *"¿Eres mayor de 18 años?"*

Si NO → Koach explica con respeto: *"Actualmente Koach está diseñado solo para mayores de 18. Cuando crezcas, te esperamos 💚"*

Si SÍ (puede mentir) → Tienes consentimiento documentado, protección parcial.

**Si detectas durante uso que es menor:**
- Suspender cuenta inmediatamente
- Contactar al usuario explicando
- Eliminar datos según LFPDPPP

**A futuro (Fase 5+):**
"Koach Junior" para 12-17 años con:
- Consentimiento parental verificable
- Protocolos especializados
- Socio nutriólogo registrado
- Aprobación de COFEPRIS si aplica

---

## 7. EDUCACIÓN EN SALUD COMO DIFERENCIADOR

*(Detallado en Sección 4 — Módulo 6)*

**Cómo aprovecharlo para el negocio:**

**Marketing de contenido:**
- Tips diarios → contenido Instagram/TikTok
- Sección Aprende → SEO en koach.mx
- Posiciona como autoridad confiable
- Atrae usuarios que buscan información

**Retención:**
- Usuario aprende algo nuevo = razón para abrir
- Tips compartibles = referidos orgánicos
- "Este coach me enseña, no solo manda recordatorios"

---

## 8. SISTEMA DE RETENCIÓN A LARGO PLAZO

### 8.1 Pivote de meta automático

Cuando Koach detecta usuario cerca de meta:
> *"¡Llegaste a tu meta! 🎉 Ahora viene mantener. ¿Pivot a mantenimiento, o nueva meta? Ganar masa, mejorar resistencia, lo que decidas."*

Convierte usuarios de "modo logro" a "modo continuidad".

### 8.2 Aniversario de 1 año

**Reporte anual personalizado** (PDF visual):
- "Empezaste pesando X, ahora pesas Y"
- Total días activos
- Total ejercicios
- Comparativa primera foto vs última
- Mensaje muy personal

**Regalo simbólico:**
- 1 mes gratis adicional
- Sticker pack temático
- Reconocimiento público

**Solicitud de testimonio formal:**
Para usar en marketing — testimonios de 1+ año son tu activo más valioso.

### 8.3 Programa de embajadores (Fase 4+)

Usuarios exitosos 1+ año:
- Comisión por referidos pagados (15-20%)
- Acceso a beta de features
- Reconocimiento público
- Material exclusivo

### 8.4 Métricas de éxito documentado

**Métricas de resultado:**
- % usuarios que alcanzan meta
- Pérdida/ganancia promedio mensual
- Cambio en medidas
- Encuesta cualitativa de impacto

**Métricas de comportamiento:**
- Días activos por mes
- Streaks promedio
- Cumplimiento de meta

**Casos de éxito documentados:**
- Banco de testimonios reales (con permiso)
- Antes/después con fotos
- Historias en video

**Mini-estudios:**
A los 6 meses: "100 usuarios de Koach: resultados promedio en 6 meses" → PR + credibilidad.

### 8.5 Comunidad y grupos (Fase 5)

**Grupos pequeños de afinidad:**
- 5-10 usuarios con metas similares
- Misma demografía/objetivos
- Koach modera

**Funcionalidad:**
- Chat grupal en app
- Compartir logros (opcional)
- Retos semanales grupales
- Tabla de progreso colectiva

**Reglas estrictas:**
- No información médica delicada
- No consejos médicos entre usuarios
- Respeto total
- Moderación automática

---

## 9. BENEFICIOS PARA USUARIOS FOUNDERS

Los primeros 50 usuarios reciben:

**Tangibles:**
- **Precio congelado vitalicio** ($149 cuando suba a $299)
- **Acceso anticipado** a todo lo nuevo
- **Voto mensual** en qué se construye
- **Sesión 1:1 con Jaziel** — 30 min/mes
- **Insignia Founder** permanente
- **Telegram privado** con cofundadores

**Emocionales:**
- **Crédito explícito** cuando contribuyen idea
- **Carta de agradecimiento** en hitos
- **Aniversario celebrado** cada año

**En marketing:**
Sección "Founders" en página web explicando estos beneficios → genera urgencia.

---

## 10. POLÍTICAS COMERCIALES Y DE SUSCRIPCIÓN

### 10.1 Cancelaciones

**Dentro del primer mes:**
- Pierde estatus founder
- Si vuelve, paga precio regular

**Después del mes 3:**
- Mantiene founder si vuelve dentro de 6 meses
- Después de 6 meses pierde estatus

**Cancelación temporal (pausa):**
- Hasta 3 meses sin perder estatus
- Después se cancela automáticamente

**Cancelaciones múltiples:**
- 2+ cancelaciones = pierde founder permanente
- Evita abuso

**Excepciones humanas:**
- Casos especiales (económico, salud) → evaluación 1-a-1
- Maira puede aprobar reactivación

### 10.2 Usuario inactivo

- 30 días sin responder → reenganche con oferta pausa
- 14 días más sin respuesta → pausa automática
- No cobra mientras esté pausado

### 10.3 Usuario que abusa

- Reportar problemas falsos
- Cancelar para no pagar
- Compartir cuenta sin upgrade
- 3 incidentes → bloqueo

### 10.4 Usuario que comparte cuenta

- 1 cuenta = 1 número WhatsApp
- Detección por patrones de uso
- Advertencia → upgrade a Plan Familia

### 10.5 Disputas de cobro

- Reembolso completo en primeros 7 días post-trial
- Después: sin reembolso pero crédito o pausa
- Política clara documentada en T&C

---

# PARTE II — ARQUITECTURA TÉCNICA

## 11. ESTRATEGIA DE IA MULTI-MODELO

### 11.1 Filosofía: cada modelo para lo que es bueno

**Capa 1 — Claude (Anthropic) — Cerebro principal**
- Onboarding conversacional
- Generación de planes personalizados
- Interpretación compleja
- Manejo de correcciones
- Conversaciones con empatía
- Detección de crisis emocionales
- **(ver ADR-007 en `docs/plan-desarrollo-sdd.md`): esta capa ahora opera con tool-use nativo, no solo generando texto — decide qué herramientas invocar**

**Capa 2 — Gemini Flash (Google) — Volumen y velocidad**
- Interpretación rápida de comidas
- Clasificación de mensajes (qué tipo es) — **alcance reducido, ver US-031 en el plan SDD**
- Extracción de datos estructurados
- Confirmaciones cortas

**Capa 3 — Whisper (OpenAI) — Audio**
- Transcripción de notas de voz
- Solo eso, ~$0.006 USD/minuto

**Capa 4 — Templates fijos — Mensajes repetitivos**
- Buenos días genéricos
- Recordatorios hidratación
- Confirmaciones simples
- Resúmenes pre-calculados
- **(ver US-038 extendida en el plan SDD: solo se usa como fallback, no como mecanismo principal de proactividad)**

### 11.2 Router — VER NOTA DE VIGENCIA

> ⚠️ El pseudocódigo de "clasificar y rutear" de esta sección quedó reemplazado
> por la arquitectura agéntica de ADR-007 (`docs/plan-desarrollo-sdd.md`). No
> implementar este router tal cual — ver US-159/US-160/US-161 en su lugar.

### 11.3 Optimización de costos

- Meta original: costo promedio por usuario activo ~$0.50 USD/mes con el router clásico
- **Corregido:** ver `docs/analisis-brechas.md` para el desglose de costos real, que incluye WhatsApp Cloud API y el gasto adicional del loop agéntico

### 11.4 Cómo comunicarlo al usuario

**En home y marketing:**
- "Coach inteligente que te conoce"
- "Tecnología que aprende de ti"
- NO "chatbot de IA"

**En página "Tecnología":**
- Explicación transparente
- Modelos usados
- Cómo se manejan datos
- Para usuarios sofisticados que valoran transparencia

---

## 12. ARQUITECTURA DE DOS SUPERFICIES

### 12.1 Roles diferenciados

**WhatsApp — Vida diaria:**
Registro, recordatorios, conversación, reacción rápida. Fricción cero.

**App — Reflexión y control:**
Ver progreso, explorar, personalizar, configurar.

### 12.2 Cómo se complementan

**De la app hacia WhatsApp:**
- Calendario de "huecos" invita a llenar registros vía WA
- Push notifications abren conversación WA
- Logros visibles cercanos generan urgencia

**De WhatsApp hacia la app:**
- Reportes generados → "velo completo en la app"
- Plan semanal → "abre la app para revisarlo"

### 12.3 Chat nativo en la app (Opción B confirmada)

**Implementación Fase 4:**
- Mismo agente, mismo contexto, diferente canal
- WebSocket para tiempo real
- Tabla `historial_conversacion` con campo `canal`
- Usuario puede empezar conversación en WA, continuar en app sin perder contexto

### 12.3bis Dashboard también disponible en web (agregado septiembre 2026, ADR-008)

Para maximizar la cobertura de mercado, el dashboard (Mi Plan, Progreso, Alacena,
Reportes) no depende exclusivamente de instalar la app nativa. Vive como rutas
autenticadas dentro del **mismo proyecto Next.js** que la landing de marketing
(`koach.mx`), de forma que cualquier persona puede entrar desde su navegador —
computadora o celular — sin instalar nada, igual que ya sucede con WhatsApp. La app
nativa (React Native + Expo) sigue construyéndose en Fase 3 como canal adicional, con
mejor experiencia para notificaciones push y cámara, pero no es requisito para usar el
dashboard. Detalle técnico completo: ADR-008 en `docs/plan-desarrollo-sdd.md`.

### 12.4 Estructura de la app móvil

**Pantalla Home:**
- Score de salud (número grande)
- Racha actual
- Próxima acción recomendada
- Resumen del día

**Sección Mi Plan:**
- Plan nutricional semanal visual
- Rutinas programadas
- Lista de compras
- Calendario de cumplimiento

**Sección Mi Koach:**
- Chat con Koach (Fase 4)
- Configuración del agente
- Centro de personalización

**Sección Progreso:**
- Gráfica de peso
- Calendario de rachas
- Logros desbloqueados
- Comparativas visuales
- Historial fotos (opcional)

**Sección Alacena:**
- Lo disponible
- Edición visual
- Recetas sugeridas

**Sección Aprende:**
- Biblioteca de contenido educativo
- Tips por categoría
- Búsqueda

**Sección Reportes:**
- PDFs generados
- Descargas históricas

**Sección Comunidad (Fase 5):**
- Grupos pequeños
- Retos

**Sección Emergencia:**
- Botón siempre accesible
- 911, SAPTEL, contacto personal

---

## 13. STACK TECNOLÓGICO COMPLETO

| Capa | Tecnología | Justificación |
|------|------------|---------------|
| Backend | Python 3.11+ + FastAPI | Asíncrono, ideal agentes |
| Cola tareas | Celery + Redis | Mensajes proactivos |
| DB | Supabase (PostgreSQL 15) | Auth + pgvector + RLS |
| IA principal | Claude API | Razonamiento, NLP complejo, tool-use (ADR-007) |
| IA velocidad | Gemini Flash | Rápido y económico |
| Voz | Whisper API (OpenAI) | Transcripción |
| Visión | Claude Vision | Análisis fotos comida (Fase 4) |
| Mensajería | WhatsApp Cloud API | Oficial Meta |
| Mapas | Google Places API | Gyms cercanos |
| App móvil | React Native + Expo | iOS/Android único código |
| Web | Next.js 14 + TypeScript + Tailwind | Robusta, SEO, gratis Vercel — **incluye el dashboard autenticado en el mismo proyecto (ADR-008)**, no solo la landing |
| Pagos | Conekta | MXN, SPEI, OXXO |
| Facturación | Facturama API | CFDI automático |
| Observabilidad | Sentry + logs estructurados | Debug producción |
| Deploy backend | Railway | Simple, económico |
| Deploy web | Vercel | Free tier suficiente |
| Storage | Supabase Storage | Fotos progreso |
| Emails | Resend | Transaccionales |
| PDFs | WeasyPrint (Python) | Generación de reportes |
| Excel | openpyxl (Python) | Reportes para usuarios técnicos |
| Analytics | PostHog | Self-hosted o cloud, gratis inicial |

> Nota: no hardcodear versiones específicas de modelo (p. ej. "claude-sonnet-4-6")
> en el código — usar siempre la configuración de `AI_SMART_PROVIDER` y el mapeo
> de modelos de `docs/plan-desarrollo-sdd.md` sección 3.4, para que cambiar de
> versión sea solo una variable de entorno.

---

## 14. BASE DE DATOS DETALLADA

**Esta sección es la fuente de verdad del esquema completo. No redefinir estas tablas en otra parte — extenderlas aquí si hace falta un campo nuevo, y documentar la migración correspondiente en `docs/plan-desarrollo-sdd.md`.**

### 14.1 Tablas principales

```sql
-- ============================================
-- USUARIOS Y EMPRESA
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(20) UNIQUE NOT NULL,  -- WhatsApp +52XXX
    email VARCHAR(255),
    password_hash VARCHAR,  -- NULL si solo WhatsApp
    created_at TIMESTAMP DEFAULT NOW(),
    plan_tier ENUM('free', 'esencial', 'coach', 'coach_plus', 'familia') DEFAULT 'free',
    trial_ends_at TIMESTAMP,
    status ENUM('active', 'paused', 'cancelled', 'trial', 'inactive') DEFAULT 'trial',
    mayor_edad_confirmado BOOLEAN DEFAULT FALSE,
    canal_preferido ENUM('whatsapp', 'app', 'ambos') DEFAULT 'whatsapp',
    es_founder BOOLEAN DEFAULT FALSE,
    referido_por_user_id UUID REFERENCES users(id),
    ip_registro VARCHAR(45),
    user_agent_registro TEXT
);

CREATE TABLE perfiles (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    nombre VARCHAR(100),
    genero ENUM('masculino', 'femenino', 'otro', 'prefiero_no_decir'),
    edad INT,
    peso_kg DECIMAL(5,2),
    peso_inicial_kg DECIMAL(5,2),
    talla_cm INT,
    meta ENUM('bajar_peso', 'ganar_musculo', 'comer_mejor', 'mas_energia', 'mantener'),
    meta_peso_kg DECIMAL(5,2),
    restricciones_alimentarias JSONB,
    alergias JSONB,
    condiciones_medicas JSONB,
    lesiones_previas JSONB,
    parq_completado BOOLEAN DEFAULT FALSE,
    parq_aprobado BOOLEAN DEFAULT FALSE,
    parq_pendiente_medico BOOLEAN DEFAULT FALSE,
    motivacion_personal TEXT,
    tono ENUM('drill', 'coach', 'amigo', 'formal') DEFAULT 'coach',
    timezone VARCHAR(50) DEFAULT 'America/Mexico_City',
    ciclo_menstrual_activo BOOLEAN DEFAULT FALSE,
    medicamentos_actuales JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE contexto_vida (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    tipo_trabajo ENUM('oficina_fijo', 'negocio_propio', 'campo', 'turnos', 'otro'),
    hora_inicio_trabajo TIME,
    hora_fin_trabajo TIME,
    cocina_para ENUM('solo', 'pareja', 'familia_2_3', 'familia_4_mas'),
    tiene_hijos BOOLEAN,
    pareja_tambien_sana BOOLEAN,
    presupuesto_semanal_mxn INT,
    actividades_fisicas_regulares JSONB,
    come_fuera_frecuencia ENUM('nunca', 'raro', 'semanal', 'varios_dias'),
    nivel_socioeconomico ENUM('bajo', 'medio_bajo', 'medio', 'medio_alto', 'alto'),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE configuracion_agente (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    horarios JSONB,
    modo_silencio_hasta TIMESTAMP,
    frecuencia_peso ENUM('semanal', 'quincenal', 'mensual') DEFAULT 'semanal',
    medidas_corporales_activas BOOLEAN DEFAULT FALSE,
    fotos_progreso_activas BOOLEAN DEFAULT FALSE,
    notificaciones_push_app BOOLEAN DEFAULT TRUE,
    notificaciones_whatsapp BOOLEAN DEFAULT TRUE,
    frecuencia_motivacional ENUM('baja', 'media', 'alta') DEFAULT 'media',
    recordatorios_medicamentos BOOLEAN DEFAULT FALSE,
    recordatorio_dormir BOOLEAN DEFAULT TRUE,
    contacto_emergencia_nombre VARCHAR(100),
    contacto_emergencia_telefono VARCHAR(20),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- NUTRICIÓN
-- ============================================

CREATE TABLE plan_nutricional (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    calorias_meta INT,
    proteina_g INT,
    carbs_g INT,
    grasas_g INT,
    agua_meta_vasos INT,
    numero_comidas INT,
    distribucion_comidas JSONB,
    version INT DEFAULT 1,
    vigente_desde DATE,
    vigente_hasta DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alacena (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    ingrediente VARCHAR(100),
    categoria ENUM('proteina', 'verdura', 'fruta', 'cereal', 'lacteo', 'grasa', 'otro'),
    cantidad DECIMAL(8,2),
    unidad VARCHAR(20),
    caducidad_aprox DATE,
    disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE plan_semanal (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    semana_inicio DATE,
    lunes JSONB, martes JSONB, miercoles JSONB,
    jueves JSONB, viernes JSONB, sabado JSONB, domingo JSONB,
    lista_compras JSONB,
    notas_especiales TEXT,
    pdf_url VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE registros_comida (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha DATE,
    tipo_comida ENUM('desayuno', 'colacion_am', 'comida', 'colacion_pm', 'cena', 'extra'),
    descripcion_original TEXT,
    descripcion_estructurada JSONB,
    calorias INT,
    proteina_g INT,
    carbs_g INT,
    grasas_g INT,
    lugar ENUM('casa', 'fuera', 'trabajo', 'restaurante', 'fonda', 'fast_food'),
    fuente_registro ENUM('texto', 'audio', 'foto', 'boton'),
    confianza_estimacion DECIMAL(3,2),
    corregido_por_usuario BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE preferencias_alimentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    alimento VARCHAR(100),
    preferencia ENUM('gusta_mucho', 'gusta', 'neutral', 'no_gusta', 'odia', 'alergia', 'intolerancia'),
    fuente ENUM('onboarding', 'correccion_usuario', 'patron_detectado'),
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- EJERCICIO
-- ============================================

CREATE TABLE plan_ejercicio (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    dias_semana JSONB,
    tipo_principal ENUM('fuerza', 'cardio', 'mixto', 'calistenia', 'funcional'),
    duracion_objetivo_min INT,
    equipamiento ENUM('gimnasio_completo', 'casa_basico', 'sin_equipo', 'mixto'),
    nivel_actual ENUM('principiante', 'intermedio', 'avanzado'),
    rutina_semanal JSONB,
    version INT DEFAULT 1,
    vigente_desde DATE,
    pdf_url VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE registros_ejercicio (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha DATE,
    tipo_sesion VARCHAR(50),
    duracion_min INT,
    completado ENUM('completo', 'parcial', 'no_realizado'),
    intensidad_percibida INT,
    lugar ENUM('gimnasio', 'casa', 'parque', 'hotel', 'otro'),
    notas TEXT,
    fuente_registro ENUM('texto', 'audio', 'boton'),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE registros_cargas_gym (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    registro_ejercicio_id UUID REFERENCES registros_ejercicio(id),
    ejercicio VARCHAR(100),
    peso_kg DECIMAL(5,2),
    series INT,
    reps_por_serie JSONB,
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ejercicios_biblioteca (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre_principal VARCHAR(100),
    nombres_alternativos JSONB,
    musculo_principal ENUM('pecho', 'espalda', 'piernas', 'hombros', 'biceps', 'triceps', 'core', 'cardio'),
    musculos_secundarios JSONB,
    nivel_minimo ENUM('principiante', 'intermedio', 'avanzado'),
    equipamiento_requerido JSONB,
    descripcion_corta TEXT,
    descripcion_detallada TEXT,
    video_url VARCHAR,
    imagen_url VARCHAR,
    errores_comunes JSONB,
    alternativas_ids JSONB
);

-- ============================================
-- AVANCES Y PROGRESO
-- ============================================

CREATE TABLE registros_agua (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha DATE,
    vasos_count INT DEFAULT 0,
    meta_vasos INT,
    UNIQUE(user_id, fecha)
);

CREATE TABLE registros_peso (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha DATE,
    peso_kg DECIMAL(5,2),
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE registros_medidas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha DATE,
    cintura_cm DECIMAL(5,2),
    cadera_cm DECIMAL(5,2),
    pecho_cm DECIMAL(5,2),
    brazo_cm DECIMAL(5,2),
    pierna_cm DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE fotos_progreso (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha DATE,
    url_supabase VARCHAR,
    tipo ENUM('frente', 'lado', 'espalda'),
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE registros_sueno (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha DATE,
    hora_dormir TIME,
    hora_despertar TIME,
    duracion_horas DECIMAL(4,2),
    calidad_subjetiva INT,
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE score_salud (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha DATE,
    score_total INT,
    subscore_nutricion INT,
    subscore_ejercicio INT,
    subscore_hidratacion INT,
    subscore_consistencia INT,
    subscore_sueno INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CONVERSACIÓN Y MEMORIA
-- ============================================

CREATE TABLE historial_conversacion (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha TIMESTAMP,
    role ENUM('user', 'assistant'),
    content TEXT,
    canal ENUM('whatsapp', 'app'),
    tipo_mensaje ENUM('proactivo', 'respuesta_usuario', 'registro', 'consulta', 'sistema'),
    tokens_used INT,
    modelo_usado VARCHAR(50),
    template_id VARCHAR(50),
    audio_url VARCHAR,
    audio_transcripcion TEXT,
    INDEX idx_user_fecha (user_id, fecha DESC)
);

-- Nota (ADR-007, docs/plan-desarrollo-sdd.md): además de esta tabla, el núcleo
-- agéntico agrega `tool_calls_log` y `acciones_pendientes` — ver US-159.

CREATE TABLE patrones_usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    patron_tipo VARCHAR(50),
    descripcion TEXT,
    datos_estructurados JSONB,
    confianza DECIMAL(3,2),
    veces_confirmado INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ciclo_menstrual (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    fecha_inicio_ciclo DATE,
    duracion_dias INT,
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- GAMIFICACIÓN
-- ============================================

CREATE TABLE rachas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    tipo ENUM('general', 'hidratacion', 'ejercicio', 'nutricion'),
    dias_actuales INT DEFAULT 0,
    mejor_racha INT DEFAULT 0,
    ultima_fecha DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE logros (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    logro_id VARCHAR(50),
    nombre VARCHAR(100),
    descripcion TEXT,
    icono_url VARCHAR,
    desbloqueado_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- SUSCRIPCIONES Y PAGOS
-- ============================================

CREATE TABLE suscripciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    plan ENUM('esencial', 'coach', 'coach_plus', 'familia'),
    status ENUM('trial', 'active', 'paused', 'cancelled', 'past_due'),
    fecha_inicio TIMESTAMP,
    fecha_renovacion TIMESTAMP,
    fecha_pausa_hasta TIMESTAMP,
    fecha_cancelacion TIMESTAMP,
    razon_cancelacion TEXT,
    conekta_customer_id VARCHAR,
    conekta_subscription_id VARCHAR,
    monto_mxn INT,
    precio_founder BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE historial_suscripciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    accion ENUM('inicio', 'renovacion', 'pausa', 'reanudacion', 'cancelacion', 'reactivacion'),
    plan_anterior VARCHAR,
    plan_nuevo VARCHAR,
    fecha TIMESTAMP DEFAULT NOW()
);

CREATE TABLE facturas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    suscripcion_id UUID REFERENCES suscripciones(id),
    cfdi_uuid VARCHAR,
    monto_total INT,
    iva INT,
    subtotal INT,
    pdf_url VARCHAR,
    xml_url VARCHAR,
    fecha_emision TIMESTAMP DEFAULT NOW()
);

CREATE TABLE referidos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_referidor_id UUID REFERENCES users(id),
    user_referido_id UUID REFERENCES users(id),
    fecha_referido TIMESTAMP DEFAULT NOW(),
    fecha_conversion TIMESTAMP,
    recompensa_otorgada BOOLEAN DEFAULT FALSE
);

-- ============================================
-- LEGAL Y COMPLIANCE
-- ============================================

CREATE TABLE consentimientos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    tipo ENUM('terminos', 'privacidad', 'datos_salud', 'comunicaciones', 'whatsapp_channel'),
    aceptado BOOLEAN,
    ip_address VARCHAR(45),
    user_agent TEXT,
    version_documento VARCHAR(20),
    fecha TIMESTAMP DEFAULT NOW()
);

CREATE TABLE solicitudes_arco (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    tipo ENUM('acceso', 'rectificacion', 'cancelacion', 'oposicion'),
    descripcion TEXT,
    status ENUM('recibida', 'en_proceso', 'completada', 'rechazada'),
    fecha_solicitud TIMESTAMP DEFAULT NOW(),
    fecha_limite TIMESTAMP,  -- +20 días hábiles
    fecha_respuesta TIMESTAMP,
    respuesta_detalle TEXT
);

CREATE TABLE logs_acceso_datos_sensibles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    accedido_por VARCHAR(100),
    tipo_acceso ENUM('lectura', 'modificacion', 'exportacion', 'eliminacion'),
    tabla_accedida VARCHAR(100),
    razon TEXT,
    ip_address VARCHAR(45),
    fecha TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- FEEDBACK Y SOPORTE
-- ============================================

CREATE TABLE feedback_usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    tipo ENUM('sugerencia', 'bug', 'queja', 'elogio', 'pregunta'),
    contenido TEXT,
    clasificacion_ia VARCHAR(100),
    prioridad ENUM('baja', 'media', 'alta', 'critica'),
    status ENUM('inbox', 'analizando', 'por_hacer', 'desarrollo', 'listo', 'rechazado'),
    respuesta_a_usuario BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE nps_respuestas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    score INT,
    categoria ENUM('detractor', 'pasivo', 'promotor'),
    comentario TEXT,
    fecha TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reportes_problemas_agente (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    mensaje_problematico_id UUID REFERENCES historial_conversacion(id),
    razon TEXT,
    revisado BOOLEAN DEFAULT FALSE,
    accion_tomada TEXT,
    fecha TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- REPORTES Y ARCHIVOS
-- ============================================

CREATE TABLE reportes_generados (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    tipo ENUM('plan_inicial', 'plan_ejercicio', 'semanal', 'mensual', 'lista_compras', 'anual'),
    formato ENUM('pdf', 'excel'),
    periodo_inicio DATE,
    periodo_fin DATE,
    url_archivo VARCHAR,
    fecha_generacion TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CONTENIDO EDUCATIVO
-- ============================================

CREATE TABLE articulos_educativos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titulo VARCHAR(200),
    slug VARCHAR(200) UNIQUE,
    categoria ENUM('nutricion', 'ejercicio', 'sueno', 'mental', 'salud_general'),
    contenido TEXT,
    fuentes JSONB,
    tiempo_lectura_min INT,
    publicado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tips_diarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contenido TEXT,
    categoria VARCHAR(50),
    nivel ENUM('basico', 'intermedio', 'avanzado'),
    activo BOOLEAN DEFAULT TRUE
);

-- ============================================
-- EVENTOS CULTURALES MÉXICO
-- ============================================

CREATE TABLE eventos_calendario_mx (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100),
    fecha_inicio DATE,
    fecha_fin DATE,
    tipo ENUM('religioso', 'patrio', 'temporada', 'familiar'),
    instrucciones_koach TEXT,
    año INT
);
```

### 14.2 Índices críticos

```sql
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_registros_comida_user_fecha ON registros_comida(user_id, fecha DESC);
CREATE INDEX idx_registros_ejercicio_user_fecha ON registros_ejercicio(user_id, fecha DESC);
CREATE INDEX idx_historial_user_fecha ON historial_conversacion(user_id, fecha DESC);
CREATE INDEX idx_alacena_user_disponible ON alacena(user_id, disponible);
CREATE INDEX idx_patrones_user ON patrones_usuario(user_id);
CREATE INDEX idx_rachas_user_tipo ON rachas(user_id, tipo);
```

### 14.3 Row Level Security (RLS) — Obligatorio

Activado en TODAS las tablas con `user_id`. Cada usuario solo accede a sus propios datos.

---

## 15. REPORTES PDF Y EXCEL

### 15.1 Reportes a generar

| Reporte | Cuándo | Formato | Fase |
|---------|--------|---------|------|
| Plan Nutricional Inicial | Onboarding | PDF | MVP |
| Plan Entrenamiento Inicial | Onboarding | PDF | MVP |
| Reporte Semanal | Domingos | PDF | Mes 2 |
| Lista de Compras | Domingos | PDF | Mes 4 |
| Reporte Mensual | Primer día del mes | PDF | Mes 6 |
| Reporte Anual | Aniversario | PDF | Mes 12 |
| Exportación completa | A solicitud | Excel | Mes 6 |

### 15.2 Generación técnica

- **PDF:** WeasyPrint (Python) con plantillas HTML+CSS
- **Excel:** openpyxl con formato profesional
- **Almacenamiento:** Supabase Storage (privado, URLs firmadas con expiración)
- **Plantillas:** Diseñadas con paleta Koach, branded, profesionales

### 15.3 Distribución

- **WhatsApp:** Envío directo como documento adjunto
- **App:** Sección "Reportes" con historial
- **Email:** Opcional para reportes mensuales/anuales

---

## 16. SISTEMA DE EJERCICIOS

*(Detallado en Sección 4 — Módulo 3)*

**MVP inicial:**
- 30-40 ejercicios base con links a YouTube
- Descripciones claras
- Sistema de alternativas por músculo

**Fase 2:**
- Expandir a 100+ ejercicios
- Videos licenciados propios o paquetes ($500-1,000 MXN)

---

## 17. BASES CIENTÍFICAS DE LAS DIETAS

### 17.1 Fórmulas y consenso científico

**A) Cálculo de TDEE**

1. **TMB (Mifflin-St Jeor):**
   - Hombres: 10×peso + 6.25×talla − 5×edad + 5
   - Mujeres: 10×peso + 6.25×talla − 5×edad − 161

2. **Factor de actividad:**
   - Sedentario: 1.2
   - Ligera: 1.375
   - Moderada: 1.55
   - Alta: 1.725
   - Muy alta: 1.9

3. **Ajuste por meta:**
   - Bajar peso: déficit 15-25% *(corregido a 20% máx. en docs/analisis-brechas.md)*
   - Mantener: TDEE exacto
   - Ganar masa: superávit 10-15%

**B) Distribución de macros**

- **Proteína:** 1.6-2.2g/kg peso corporal
- **Grasas:** 20-30% calorías totales (mín 0.8g/kg)
- **Carbohidratos:** el resto

**C) Reglas de seguridad**

- Nunca <1,200 kcal mujeres ni <1,500 kcal hombres sin supervisión médica *(corregido a 1,400/1,700 en docs/analisis-brechas.md)*
- Nunca pérdidas >1% peso corporal/semana *(corregido a 0.75% en docs/analisis-brechas.md)*
- Considerar restricciones SIEMPRE
- Condición médica seria → derivar a profesional

### 17.2 Validación profesional

**Ya no es "mes 3-6, nice to have"** — ver `docs/adenda-legal-pendientes.md`: es requisito antes de cobrar el primer peso.

### 17.3 Comunicación legal al usuario

> *"Koach utiliza fórmulas científicamente validadas (Mifflin-St Jeor, OMS) para calcular tus necesidades. No sustituye consulta con nutriólogo registrado, especialmente si tienes condiciones médicas."*

---

# PARTE III — SEGURIDAD Y COMPLIANCE

## 18. WHATSAPP CLOUD API — REGLAS CRÍTICAS

### 18.1 Categoría wellness/fitness

✅ **Permitido:**
- Recordatorios rutina y nutrición
- Mensajes informativos hábitos
- Coaching fitness y nutrición

⚠️ **Cuidado con:**
- Vocabulario médico (revisión lenta)
- No prescribir ni diagnosticar

❌ **Prohibido:**
- Vender medicamentos/suplementos
- Promesas de cura
- Mensajes sin consentimiento

### 18.2 Templates obligatorios

Mensajes proactivos = templates aprobados por Meta (fallback — ver US-038 extendida, el contenido principal ahora lo decide el loop agéntico).

**~25 templates iniciales:**

```
buenos_dias_general / drill / coach / amigo
recordatorio_desayuno
recordatorio_colacion_am / pm
sugerencia_comida
recordatorio_agua
checkin_ejercicio
checkin_cena
resumen_dia_general
resumen_semanal_domingo
reenganche_3_dias
oferta_extension_prueba
felicitacion_racha_7 / 30 / 90 / 365
recordatorio_peso_lunes
recordatorio_medidas_mensual
recordatorio_foto_progreso
plan_semanal_listo
lista_compras_lista
recordatorio_dormir
recordatorio_medicamento
oferta_renovacion
```

**Tips aprobación:**
- "Revisar" sí, "examinar" no
- "Hábito" sí, "tratamiento" no
- "Seguimiento" sí, "diagnóstico" no
- 2 variantes por template (backup)

### 18.3 Política IA Meta

Koach es agente especializado, NO de propósito general. Protegido.

### 18.4 Número dedicado

- Chip exclusivo (~$100 MXN)
- Permanente — cambiar = perder historial
- Registrado en Meta Business Manager

---

## 19. LFPDPPP 2025 — CUMPLIMIENTO LEGAL

### 19.1 Consentimiento expreso datos sensibles

Datos de salud requieren consentimiento expreso por escrito (firma electrónica).

**Implementación:**
- Pantalla específica antes de pedir datos de salud
- Usuario escribe "ACEPTO" o presiona botón confirmación
- Guardar en tabla `consentimientos` con timestamp, IP, versión

### 19.2 Aviso de Privacidad completo

Incluye:
- Responsable (Maira Anguiano / Koach Technologies)
- Datos recabados y finalidad
- Terceros (Anthropic, Google, Meta, Supabase)
- Derechos ARCO
- Servidores en EE.UU.
- Cambios y notificación

### 19.3 Derechos ARCO funcionales

**Comandos WhatsApp:**
- `MIS DATOS` → resumen
- `BORRAR MIS DATOS` → cancelación
- `RECTIFICAR [dato]` → corrección
- `EXPORTAR MIS DATOS` → ZIP completo

**Tiempo respuesta:** 20 días hábiles por ley.

### 19.4 Documentos legales antes de lanzar

1. Aviso de Privacidad LFPDPPP 2025
2. Términos y Condiciones por tier
3. Disclaimer médico
4. Política de cancelación
5. Política de uso aceptable

**Costo asesoría legal:** $5,000-$10,000 MXN una vez.

---

## 20. SEGURIDAD TÉCNICA Y DATOS SENSIBLES

### 20.1 Datos en reposo

- Supabase: cifrado AES-256 automático
- RLS activado en todas las tablas
- Backups diarios automáticos + semanal manual redundante
- Datos médicos especialmente sensibles: cifrado adicional aplicación

### 20.2 Datos en tránsito

- HTTPS obligatorio en TODOS los endpoints
- SSL automático Vercel/Railway
- WhatsApp ya cifra E2E
- TLS 1.3 para APIs

### 20.3 Gestión de secretos

**NUNCA en código:**
- API keys
- Tokens WhatsApp
- Conexiones DB
- Conekta keys

**Solución:**
- Variables de entorno Railway/Vercel
- `.env` solo local en `.gitignore`
- Rotación cada 90 días

### 20.4 Acceso administrativo

- Solo Jaziel acceso completo
- Maira solo métricas agregadas
- Logs de cada acceso a datos sensibles
- Principio de mínimo privilegio

### 20.5 Plan de respuesta a incidentes

Si ocurre brecha:
1. Notificación a usuarios en 72 horas (LFPDPPP)
2. Reporte a autoridad
3. Análisis forense
4. Plan de remediación

Documentar ANTES de tener usuarios.

---

## 21. PROTECCIÓN DEL AGENTE IA

### 21.1 Capas de seguridad del agente

**Capa 1 — System prompt blindado**
Reglas no negociables que Claude siempre sigue.

**Capa 2 — Validación de outputs**
Antes de enviar mensaje, otro filtro verifica:
- ¿Diagnóstico médico? → bloquear
- ¿Recomienda medicamento? → bloquear
- ¿Promete curar? → bloquear
- ¿Calorías por debajo de mínimos? → bloquear
- ¿Ejercicio peligroso para condición declarada? → bloquear

**Capa 3 — Lista de palabras bloqueadas**
Detección de medicamentos específicos, diagnósticos → regenerar.

**Capa 4 — Revisión humana**
Tú revisas logs semanales marcados como sensibles.

**Capa 5 — Reportes de usuarios**
Comando "REPORTAR" en WhatsApp.

> **Capa 6 (agregada, ADR-007):** validación determinista en cada función de dominio detrás de una tool sensible, y patrón "propone → confirma" — ver `docs/plan-desarrollo-sdd.md`.

### 21.2 Protección contra ataques

- Rate limiting por usuario
- Detección prompt injection
- Protección DDoS Vercel/Railway
- Validación estricta inputs

---

## 22. PROTOCOLOS DE EMERGENCIA

### 22.1 Crisis emocional/suicidio

**Detección automática:**
"Ya no quiero", "para qué", "todo da igual", "ya no puedo", "quiero desaparecer".

**Respuesta inmediata:**
> *"Oye, lo que me dices me preocupa de verdad. Antes de cualquier cosa de fitness, ¿estás bien? ¿Estás teniendo pensamientos de hacerte daño?"*

Si confirma:
> *"Por favor habla con alguien capacitado. SAPTEL: 55 5259-8121, 24/7. O 911. ¿Quieres que te ayude a contactar a alguien?"*

**No es trabajo de Koach resolver — es derivar.**

### 22.2 Emergencia médica física

**Detección:**
"Dolor pecho", "no puedo respirar", "me siento muy mal", "no puedo moverme".

**Respuesta inmediata:**
> *"Eso suena serio — llama al 911 ahora. Yo aquí estaré."*

---

## 23. BOTÓN DE EMERGENCIA Y CRISIS

### 23.1 En la app (Fase 3)

Botón "Emergencia" siempre visible:
- **Opción 1:** Llamar 911 directo
- **Opción 2:** Llamar SAPTEL (línea emocional)
- **Opción 3:** Llamar contacto de emergencia personal
- **Opción 4:** Llamar Cruz Roja 065

### 23.2 Contacto de emergencia configurable

En onboarding o configuración:
- Nombre y teléfono contacto emergencia
- Médico tratante (opcional)

### 23.3 Tarjeta médica (Fase 4)

Información accesible desde lock screen:
- Alergias
- Medicamentos
- Condiciones
- Tipo sangre
- Contacto emergencia

Para emergencias reales (similar a iOS Health).

---

# PARTE IV — MARKETING Y CRECIMIENTO

## 24. ESTRATEGIA DE MARKETING

### 24.1 Pilares de marketing

**Pilar 1 — Contenido educativo (orgánico):**
Tips diarios, blog en koach.mx, reels educativos. Posiciona como autoridad.

**Pilar 2 — Casos de éxito:**
Testimonios reales, antes/después, historias. Convencen más que cualquier anuncio.

**Pilar 3 — Comunidad local Colima:**
Red personal, gimnasios locales, partnerships, eventos.

**Pilar 4 — Referidos:**
Sistema integrado. Embajadores Fase 4+.

**Pilar 5 — Transparencia:**
Compartir crecimiento, aprendizajes, errores. Construye confianza.

### 24.2 Canales por fase

**Mes 1-3:**
- Red personal Colima/Villa de Álvarez
- Instagram + TikTok orgánico
- Grupos locales Facebook/WhatsApp

**Mes 4-6:**
- Partnerships con gimnasios
- Sistema de referidos activo
- Blog SEO empezando

**Mes 7-12:**
- TikTok ads pequeños presupuesto
- PR local (medios Colima)
- Programa embajadores

**Mes 12+:**
- Expansión LATAM con marketing pagado
- Influencers fitness mexicanos
- Eventos propios

---

## 25. PÁGINA WEB ROBUSTA

### 25.1 Tecnología

**Next.js 14 + TypeScript + Tailwind + Vercel**

- SEO desde día 1
- Server-side rendering
- App router moderno
- Componentes reutilizables
- Deploy automático desde GitHub
- Gratis (Vercel free tier)

### 25.2 Estructura completa

```
/                        Home/Landing
/como-funciona          Explicación profunda
/precios                Tabla comparativa
/historias              Casos de éxito
/blog                   Contenido SEO
/recursos               Guías descargables
/sobre-nosotros         Historia, misión
/founders               Página exclusiva founders
/tecnologia             Transparencia técnica/IA
/preguntas-frecuentes   FAQ extensa
/contacto               Formulario + WhatsApp
/privacidad             Aviso LFPDPPP
/terminos               T&C
/disclaimer-medico      Disclaimer formal
```

### 25.3 Componentes del Home

**Hero:**
- Título: "Tu coach de salud por WhatsApp"
- Subtítulo: "Te acompañamos todos los días para ser más saludable"
- CTA: "Empezar gratis 7 días" → WhatsApp con mensaje pre-llenado
- Mockup conversación animado

**Sección Problema:**
3 puntos: por qué apps de fitness fallan.

**Sección Solución:**
3 pasos: Onboarding → Acompañamiento → Resultados.

**Sección "Cómo funciona":**
Video corto 60 seg + demos visuales.

**Sección Para quién:**
- Lista perfiles que ayuda
- Lista "para quién no es" (genera confianza)

**Sección Precios:**
Tabla comparativa con plan Founder destacado.

**Sección Testimoniales:**
3-5 reales con foto y nombre (cuando los tengas).

**Sección Educación:**
Tips destacados del blog (SEO + autoridad).

**Sección FAQ:**
10 preguntas honestas (privacidad, cancelación, qué pasa si no funciona).

**Sección Founders:**
Beneficios exclusivos de los primeros 50.

**CTA Final:**
"Empezar prueba gratuita" → WhatsApp.

### 25.4 Optimización

- Core Web Vitals
- Lazy loading imágenes
- Optimización móvil (>90% tráfico)
- Schema.org structured data
- Open Graph para redes sociales
- Pixel de Facebook/Meta (Fase 3 para ads)

---

## 26. ROL DE MAIRA Y PLAN EDITORIAL

### 26.1 Responsabilidades

**Construcción de marca:**
- Voz, tono, identidad visual
- Consistencia en superficies
- Curaduría visual

**Contenido:**
- 3 reels/TikTok semanales
- 5 posts Instagram semanales
- Stories diarias
- Mix: educativo + casos reales + behind the scenes

**Gestión de comunidad:**
- DMs y comentarios
- Consultas pre-venta
- Lista de email
- Grupos privados founders

**Captación directa:**
- Comunidades locales
- Conocidos
- Gimnasios
- Eventos

### 26.2 Calendario editorial sugerido

| Día | Tema |
|-----|------|
| Lunes | Motivacional / "Empieza tu semana" |
| Martes | Tip nutrición mexicana |
| Miércoles | Reel: Caso de uso real |
| Jueves | Tip de ejercicio |
| Viernes | Behind the scenes / construyendo Koach |
| Sábado | Testimonio o resultado |
| Domingo | Reflexión / preparación semana |

### 26.3 Herramientas Maira

- Canva Pro: $300 MXN/mes
- Capcut: gratis (edición video)
- Meta Business Suite: gratis (programar posts)
- Notion: gratis (calendario editorial)

---

## 27. SISTEMA DE RETROALIMENTACIÓN

### 27.1 Cuatro canales

**Canal A — Feedback continuo WhatsApp**
Koach pregunta naturalmente cada 2-3 semanas. Guarda en `feedback_usuario` con clasificación automática.

**Canal B — NPS quincenal**
Escala 1-10:
- 1-6: detractor → preguntar qué falla
- 7-8: pasivo → preguntar qué haría dar 10
- 9-10: promotor → pedir compartir

**Canal C — Encuesta cancelación**
1 sola pregunta: *"¿Qué nos faltó?"*. Oro puro.

**Canal D — Llamadas 1:1 founders**
Mensual, 15-30 min. Solo primeros 6 meses.

### 27.2 Procesamiento

Tablero GitHub Projects:
- 📥 Inbox
- 🔍 Analizando
- 📋 Por hacer
- 🛠️ Desarrollo
- ✅ Listo
- ❌ Rechazado (con razón)

**Acción clave:** Cuando construyas algo pedido, avisar al usuario personalmente → convierte en evangelista.

---

## 28. COMUNICACIÓN DE FUNCIONALIDADES

### 28.1 En la app — Onboarding visual

Primera vez:
- Tour de 4-5 pantallas
- Saltable
- Animaciones simples

### 28.2 En WhatsApp — Mensaje "Conoce a Koach"

Después de onboarding completado:
> *"Listo, ya somos equipo 💪 Te cuento qué puedo hacer:*
> *🍽️ Plan nutricional personalizado*
> *💪 Rutinas adaptadas*
> *🛒 Lista de compras semanal*
> *📊 Reportes de tu progreso*
> *🍴 Ayuda cuando comes fuera*
> *🏋️ Videos de ejercicios*
> *💤 Recordatorios de sueño*
> *📚 Tips de salud diarios*
> *⚠️ No soy médico — para condiciones, consulta profesional*
> *Escribe AYUDA para verlo otra vez."*

### 28.3 Sistema de comandos

Comandos escritos en WhatsApp:
- `AYUDA` → ver todo
- `PLAN` → plan del día
- `ALACENA` → gestionar alacena
- `COMPRAS` → lista compras
- `PROGRESO` → ver avances
- `CAMBIAR TONO` → ajustar personalidad
- `PAUSA` → pausar mensajes
- `MIS DATOS` → ver qué guarda Koach
- `BORRAR MIS DATOS` → eliminar cuenta
- `REPORTAR` → reportar problema

### 28.4 Descubrimiento progresivo

Cada semana, Koach revela funcionalidad relevante. Evita abrumar al inicio.

---

# PARTE V — MODELO DE NEGOCIO

## 29. PRICING Y PLANES

*(ver nota de vigencia: precio en duda, pendiente de confirmar con más entrevistas)*

### 29.1 Estructura actualizada

| Plan | Precio | Incluye |
|------|--------|---------|
| **Free** | $0 | 7 días prueba completa |
| **Esencial** | $149 MXN/mes | Plan + sugerencias, sin proactividad completa |
| **Coach** | $299 MXN/mes | Todo + agente proactivo + voz + reportes + chat app |
| **Coach Plus** | $449 MXN/mes | Coach + sesión 1:1 mensual + Google Calendar + acceso anticipado |
| **Familia** | $599 MXN/mes | Hasta 4 perfiles (Fase 5) |

### 29.2 Precio Founder

Primeros 50 usuarios → **Plan Coach a $149 MXN/mes vitalicio**

Incluye todos los beneficios futuros automáticamente.

### 29.3 Política de cobro

- Conekta para todos los métodos
- Tarjeta, SPEI, OXXO Pay
- Domiciliación automática
- CFDI automática por suscripción

### 29.4 Reembolsos

- 7 días post-trial: reembolso completo
- Después: sin reembolso, ofrecer pausa o crédito

---

## 30. PROYECCIÓN FINANCIERA

*(ver nota de vigencia: costos de WhatsApp corregidos en docs/analisis-brechas.md — estas cifras son las originales, no las actuales)*

### 30.1 Inversión inicial

| Concepto | MXN |
|----------|-----|
| Dominios (koach.mx + koach.app) | $750 |
| Chip WhatsApp dedicado | $100 |
| Logo profesional | $1,500 |
| Canva Pro (anual) | $1,200 |
| Asesoría legal documentos | $7,000 (mes 2) |
| **Total inicial** | **~$10,550 MXN** |

(Distribuido: $3,550 semana 1, $7,000 mes 2 cuando hay ingresos)

### 30.2 Costos operativos mensuales (originales, ver corrección en docs/analisis-brechas.md)

**Mes 1 (0-5 usuarios):**
| Servicio | MXN |
|----------|-----|
| Supabase Free | $0 |
| Vercel Free | $0 |
| Railway básico | $200 |
| Claude API | $100 |
| WhatsApp Cloud API | $0 |
| **Total** | **~$300** |

**Mes 2-3 (15-30 usuarios):**
| Servicio | MXN |
|----------|-----|
| Supabase Free→Pro | $500 |
| Railway | $500 |
| Claude API | $800 |
| Gemini API | $200 |
| Whisper API | $100 |
| WhatsApp API | $0 |
| Canva Pro | $300 |
| Google Places API | $50 |
| **Total** | **~$2,450** |

### 30.3 Proyección 12 meses (original, pendiente de re-hacer con costos corregidos)

| Mes | Usuarios | Ingresos | Costos | Neto mes | Acumulado |
|-----|----------|----------|--------|----------|-----------|
| 1 | 5 beta | $0 | $3,850 | -$3,850 | -$3,850 |
| 2 | 20 | $2,000 | $9,450* | -$7,450 | -$11,300 |
| 3 | 35 | $3,800 | $2,450 | +$1,350 | -$9,950 |
| 4 | 55 | $6,500 | $2,800 | +$3,700 | -$6,250 |
| 5 | 80 | $9,500 | $3,200 | +$6,300 | +$50 |
| 6 | 110 | $13,000 | $3,800 | +$9,200 | +$9,250 |
| 9 | 200 | $28,000 | $5,500 | +$22,500 | +$70,000 |
| 12 | 350 | $52,000 | $7,500 | +$44,500 | +$190,000 |

*Mes 2 incluye asesoría legal $7,000

### 30.4 Break-even

- **Operacional:** 8-10 usuarios Coach (~$1,500-2,500 MXN ingresos)
- **Total acumulado positivo:** Mes 5
- **Rentable mensual:** Mes 3

---

## 31. MÉTRICAS DE ÉXITO

### 31.1 Producto

| Métrica | Meta MVP | Meta 6m |
|---------|----------|---------|
| Onboarding completion día 1 | >70% | >80% |
| Activos a 7 días | >60% | >75% |
| Activos a 30 días | >40% | >60% |
| Interacciones/día/usuario | >4 | >6 |
| Respuesta proactivos | >50% | >70% |
| Conversión trial → pago | >30% | >50% |

### 31.2 Negocio

| Métrica | Meta 3m | Meta 12m |
|---------|---------|----------|
| MRR | $3,500 | $52,000 |
| Churn mensual | <8% | <5% |
| CAC | <$100 | <$150 |
| LTV | >$1,500 | >$3,500 |
| NPS | >40 | >55 |

### 31.3 Señales product-market fit

- >40% trial → pago
- >40% usuarios 90+ días activos
- >20% nuevos por referido orgánico
- Usuarios dicen "no puedo sin Koach"

---

## 32. RIESGOS Y MITIGACIONES

| Riesgo | Prob | Impacto | Mitigación |
|--------|------|---------|------------|
| Meta cambia políticas | M | A | Chat app desde Fase 4 |
| Costos IA escalan | M | M | Multi-modelo + templates + caché + circuit breaker (US-134) |
| Usuario reporta daño | B | A | PAR-Q + disclaimers + validación nutriólogo |
| Competidor copia | M | M | Contexto MX + conocimiento acumulado |
| Sanción LFPDPPP | B | A | Documentación + abogado |
| Templates rechazados | A | M | 2x backup |
| Churn alto | M | M | Onboarding optimizado + reportes |
| Tiempo de Jaziel | A | M | Maira marketing + SDD eficiente |
| Cofundadores se desincronizan | B | A | Acuerdo escrito |
| Cambios en LFPDPPP | B | A | Revisión legal semestral |

---

# PARTE VI — EJECUCIÓN

## 33. METODOLOGÍA SDD

### 33.1 Spec-Driven Development

Flujo: **Spec → Plan → Tasks → Implement**

1. **Spec** — Documento detallado de qué debe hacer
2. **Plan** — Claude propone cómo construir
3. **Tasks** — Desglose en pasos atómicos
4. **Implement** — Ejecución supervisada

### 33.2 Estructura del proyecto — VER NOTA

> Esta estructura de carpetas es la original. La estructura real vigente
> (con arquitectura hexagonal completa) está en `docs/plan-desarrollo-sdd.md`
> sección 4 — es más detallada y es la que se usó para el scaffold real.

### 33.3 Herramientas

| Herramienta | Rol | Costo |
|---|---|---|
| Claude Pro / Claude Code | SDD | Ya tienes |
| VS Code | Editor | Gratis |
| GitHub + Projects | Repo + tareas | Gratis privado |
| Notion | Documentación viva | Gratis |
| Supabase | DB + Auth | Free → $25/mes |
| Vercel | Web | Gratis |
| Railway | Backend | $5-10/mes |

### 33.4 Flujo de trabajo — VER NOTA

> El flujo semanal/calendario descrito originalmente aquí quedó reemplazado
> por el enfoque de horas-por-hito sin calendario fijo — ver
> `docs/plan-desarrollo-secuencial.md`.

### 33.5 Separación Sittek/Koach

- Koach SOLO en laptop personal
- Sittek SOLO en laptop empresa
- Misma cuenta Claude Pro (válido)
- Mismo GitHub cuenta personal
- Cero recursos Sittek para Koach

---

## 34. PLAN DE DESARROLLO POR FASES — VER NOTA

> El plan de fases por semanas de esta sección quedó reemplazado por el
> plan de hitos por horas (M1-M12 para Fase 0-1) en
> `docs/plan-desarrollo-secuencial.md`. Los NOMBRES de fase (Fase 0-5) y su
> CONTENIDO conceptual siguen siendo válidos como panorama general; el
> ORDEN Y LAS HORAS exactas están en el documento secuencial.

### FASE 0 — Setup y Validación — 30 hrs total (panorama, ver secuencial para detalle)

- Configuración total del entorno
- Página web base
- Tablas iniciales Supabase
- Validación con usuarios reales
- Templates Meta enviados

### FASE 1 — MVP WhatsApp — 80 hrs (panorama; real ≈172 hrs con seguridad + núcleo agéntico, ver secuencial)

- Backend FastAPI completo
- WhatsApp Cloud API conectada
- Onboarding por WhatsApp funcionando
- Generación de planes con Claude
- Registro de comidas y ejercicio
- Mensajes proactivos, rachas, reportes básicos

### FASE 2 — Nutrición Completa — 80 hrs

- Alacena inteligente
- Modelo conversacional de negociación de comidas (reemplaza plan semanal fijo)
- Lista de compras
- Modo "Comí Fuera"
- Audios (Whisper)
- Calendario cultural MX

### FASE 3 — App Móvil + Dashboard — 80 hrs

- React Native app
- Dashboard con todas las secciones
- Score de salud
- Reportes mensuales
- Modo gym avanzado
- Notificaciones push

### FASE 4 — Chat en App + Monetización — 80 hrs

- WebSocket chat tiempo real
- Conekta automatizado
- Sistema de referidos
- Google Calendar integration
- Análisis de fotos comida

### FASE 5 — Crecimiento (Semana 33+)

- Modo familia
- Comunidad grupos
- Programa embajadores
- Expansión LATAM
- Migración a SAS si aplica

---

## 35. ROADMAP FUTURO (FASE 4+)

**Mes 6-12:**
- App móvil completa
- Chat nativo en app
- Pagos automatizados
- Análisis fotos
- Google Calendar

**Mes 12-18:**
- Modo familia
- Comunidad y grupos
- Programa embajadores
- Migración SAS
- Nutriólogo en equipo

**Mes 18-24:**
- Expansión a otras ciudades MX
- Marketing pagado
- Koach Junior (con socio profesional)
- Wearables integration (Apple Watch, Fitbit)
- API pública para gimnasios

**Mes 24+:**
- Expansión LATAM
- Equipo de 10+ personas
- Posible inversión Serie A
- Productos B2B (gimnasios, empresas)

---

## RESUMEN EJECUTIVO

**Koach** es un agente de salud proactivo para mexicanos, operando en WhatsApp + App con tecnología multi-IA (ahora agéntica, ver ADR-007) y contexto cultural mexicano.

**Equipo:** Jaziel (CTO) + Maira (CEO) cofundadores.

**Estructura legal:** Persona Física RESICO PF inicialmente, SAS al año.

**Diferenciadores únicos:**
- Proactividad WhatsApp
- Conocimiento acumulado del usuario
- Contexto cultural MX
- Educación en salud integrada
- Multi-IA optimizada, ahora con tool-use nativo
- Equipo local Colima

---

*Koach — Plan Maestro v6.0 Definitivo (con nota de vigencia agregada en septiembre 2026)*
*Mayo 2026*
*Cofundadores: Jaziel + Maira Anguiano*
