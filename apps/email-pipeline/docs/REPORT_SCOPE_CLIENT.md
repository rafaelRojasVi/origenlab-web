# Alcance del informe de correo (para cliente)

## ¿Qué es **rebote / NDR**?

- **NDR** (*Non-Delivery Report*) = aviso automático de que un correo **no pudo entregarse** (buzón lleno, dirección mal escrita, servidor rechazó, etc.).
- En la práctica lo envía **Mailer-Daemon**, **postmaster** o el propio servidor con asuntos del tipo *Delivery Status Notification*, *Undeliverable*, *Mail delivery failed*.
- **No son conversaciones de negocio**: inflan volumen y dominios como el del hosting de correo. Por eso el informe los etiqueta aparte y ofrece rankings **sin** esos remitentes.

---

## ¿Es lo bastante específico?

**Para “qué dice el archivo de correo” → sí, es útil y bastante específico.**  
Volumen, años, rebotes, mezcla cotización/OC/factura/universidad, dominios y menciones de equipamiento dan una foto clara del **contenido del buzón**, no del negocio contable al 100%.

**Para “qué se vendió más” o “qué modelo” → no; este informe no puede sustituir eso.**  
Lo que ves son **menciones de palabras** (y dominios). Eso no es:

- unidades vendidas  
- modelo exacto más vendido  
- margen ni ticket  

Un correo puede decir “balanza” 20 veces en un hilo y no haber venta; otro puede cerrar una OC sin repetir la palabra del equipo en asunto/cuerpo indexado.

---

## ¿Pedir más tipo “modelo”, “más usado”, “más vendido”?

| Pregunta | Desde solo este mail | Mejor fuente |
|----------|----------------------|--------------|
| **Más vendido** | Mala proxy | Facturas, ERP, OCs en PDF/Excel si las tienen |
| **Modelo / marca concreta** | Posible como **“más mencionado”** (ruidoso) | Catálogo + regex por familia; o extracción manual en muestra |
| **Cliente / canal fuerte** | Mejor con **To/Cc excl. dominio propio** + sin NDR | Tabla “Contrapartes (Para/Cc)” del informe |
| **Qué equipo “pide” el mercado** | Tablas de equipamiento + **cotización ∧ equipo** | Señal de conversación, no ventas |

Si al cliente le interesa **“más vendido”**, lo honesto es: *“El informe de correo mide conversación y temas; para ‘más vendido’ necesitamos facturación o OCs.”*  
Si les basta **priorizar marketing o stock por interés en el hilo**, entonces sí tiene sentido ampliar el informe con cosas **derivables del texto**, con el disclaimer de “menciones, no unidades”.

---

## Qué añade el informe (sin prometer “ventas”)

1. **Top contrapartes** — dominios en Para/Cc **excluyendo** el dominio del buzón (p. ej. `labdelivery.cl`), para no inflar todo en la cuenta propia.  
2. **Remitentes operativos** — mismos rankings excluyendo Mailer-Daemon / avisos de entrega.  
3. **Cruces** — mensajes que son **cotización y** mencionan X equipo (proxy de “de qué se cotiza”).  
4. **Volumen por año (solo cotización)** — cuántos hilos/mensajes mencionan cotización por año.

En una frase: **el informe es bueno para volumen, temas y red de contacto; para modelo más vendido o ranking de ventas hace falta otro dato (facturación/OC), y el mail solo puede aproximar “de qué se habla más”.**
