# Calculation Methodology

## Formula

```
custo_base = distancia_km * custo_km_base * fator_modal

adicional_peso =
    if peso_kg <= capacidade_kg: 0
    else: (peso_kg - capacidade_kg) * taxa_excesso_kg

seguro = max(valor_carga * fator_seguro, seguro_minimo)

adicional_risco = custo_base * (fator_risco - 1)

subtotal = custo_base + custo_fixo_operacional + carga_descarga_base
           + adicional_peso + seguro + adicional_risco

taxa_administrativa = subtotal * taxa_administrativa_percentual

frete_estimado = max(subtotal + taxa_administrativa, frete_minimo)
```

## Business Rules

1. The municipality must be identified by the official IBGE code.
2. The calculation uses distances between municipal seats, not street-level addresses.
3. When a road distance is available, it takes priority over other modals.
4. When no road route exists, waterway or air modal can be selected.
5. The cost per km depends on the vehicle type.
6. The cargo type changes the risk factor and insurance factor.
7. The cargo value is used only for insurance calculation.
8. Weight exceeding vehicle capacity generates a per-kg surcharge.
9. The freight total can never be less than the minimum freight for the selected vehicle.
10. Every simulation generates a full calculation memory with item, value, and source.

## Parameters

All parameters are stored as editable CSV files in `data/`.

- `parametros_veiculos.csv` — vehicle types, capacity, cost per km, minimum freight
- `parametros_cargas.csv` — cargo types, risk factor, insurance factor
- `parametros_modal.csv` — modal types and modal factor
- `adicionais.csv` — fixed operational costs, administrative rate, insurance minimum, excess kg rate
