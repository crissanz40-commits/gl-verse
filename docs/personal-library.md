# Lista y seguimiento personal

La lista personal guarda información subjetiva de visionado sin modificar el catálogo. Cada entrada pertenece a la combinación del `google_sub` autenticado y una serie.

## Estados

- `want_to_watch`: quiero verla; sirve como lista de pendientes.
- `watching`: viendo actualmente.
- `watched`: vista o terminada.
- `paused`: empezada, pero en pausa.
- `dropped`: abandonada.

El progreso es un contador de episodios vistos. Cuando el catálogo conoce el total de episodios, la API impide superarlo; si todavía no lo conoce, permite un contador manual. La puntuación personal usa enteros de 1 a 10: es una escala compacta, inequívoca y fácil de comparar. La ausencia de nota es distinta de una puntuación baja.

La opinión es privada y opcional, con un máximo de 2000 caracteres. Las fechas de inicio y finalización también son opcionales; si se indican ambas, la finalización no puede ser anterior al inicio. `created_at` conserva cuándo se añadió la serie y `updated_at` permite ordenar la actividad reciente.

## API y privacidad

- `GET /api/me/library` devuelve únicamente la lista de la sesión activa.
- `PUT /api/me/library/{series_id}` crea o sustituye una entrada.
- `DELETE /api/me/library/{series_id}` elimina el seguimiento de esa serie.

No se acepta un identificador de usuario en rutas ni cuerpos. El servidor obtiene `user_sub` de la sesión validada. Las mutaciones exigen además el token CSRF de esa sesión. Tanto viewers como admins pueden gestionar su propia lista, sin acceso especial del administrador a los datos personales de otras cuentas.

La migración `014_personal_series_library.sql` crea `user_series_entries` separada de las tablas objetivas. Sus claves foráneas eliminan entradas huérfanas si desaparece la cuenta o la serie, y su clave primaria evita duplicados por usuario y serie.
