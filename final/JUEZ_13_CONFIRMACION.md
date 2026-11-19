# Confirmación independiente del juez

Abrir `ContractRisk_Final_Juez_13_Confirmacion_Colab.ipynb` en Colab con **CPU**,
habilitar los dos secretos existentes y ejecutar una sola vez, en orden. Usar la
misma cuenta de Drive, proyecto de prepago y carpeta de presupuesto. Mantener
recarga automática desactivada y no consumir la API desde otra aplicación.
Confirmar `CONFIRMACION_MAXIMO_5_USD` solo si esas condiciones se mantienen.

No repetir Juez 12. La confirmación no lo recalifica: usa los doce casos que el
usuario aprobó antes de la inferencia. Exige 12/12 válidos, al menos 11/12 dentro
del rango y ninguna respuesta mala con 4–5, sin cambiar los criterios. Las
etiquetas/rangos de evaluación no se envían al juez. Un fallo API o una respuesta
mala aprobada detiene la corrida, sin reintentos técnicos ni selección de notas.

Se verifican seis marcadores y los 45 asientos iniciales por USD 4,0800825
estimados/reservados. Presupuesto TOTAL USD 5. Cada petición debe poder reservar
USD 0,6144; ante error conserva su reserva. Tras éxito actualiza solo esa petición
según uso. El margen inicial USD 0,9199175 no garantiza completar doce casos:
si no alcanza para la siguiente reserva, se detiene, sin borrar ni liberar
reservas desconocidas. No hacen falta más recargas para preparar esta prueba.

Al terminar, ejecutar inspección y descarga y devolver ZIP y notebook con salidas.
Si falla, no repetir; solo ejecutar las celdas finales para conservar evidencia.
Aunque pase, mantiene `judge_validated_for_final=false` hasta auditar motivos.
No califica aún el producto ni abre automáticamente la siguiente etapa de gasto.
Tarifas vigentes comprobadas 19/11/2026, revisión requerida después de 20/11 UTC.

La [calibración 12 y su auditoría](evidence/paid_12/ANALISIS.md) se conservan
intactas. Esta preparación no ejecuta consultas pagadas ni modifica main o Space.
