# Memoria de Calculo

Every simulation performed in frete-calculo-br generates a calculation memory table displayed directly in the interface.

The memory contains the following fields:

| Field | Description |
|---|---|
| item | Name of the cost component or parameter |
| valor | Numeric value applied in the calculation |
| fonte | Data source or file from which the value was obtained |

All items in the formula are traced back to their source CSV file or identified as a derived calculation step.

This design ensures the estimate is fully auditable and reproducible.
