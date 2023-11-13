## fiscalIA
# Clase "wordsMagic"

Dado un input de palabras, hace dos cosas:

1) Le pone un índice a las palabras
2) wordsMagic.match(INPUT) --> match, matchErr: Hace matching de la lista de palabras contra INPUT
	:: El macheo puede ser exacto, se devuelve en match
	:: O contener una diferencia (impreciso), que se devuelve en matchErr

Una diferencia o imprecisión se define como alguna de las siguiente condiciones:
	:: Un caracter de más: "FernáXdez" machea con "Fernández"
	:: Un caracter de menos: "Fern_dez" machea con "Fernández"
	:: Un intercambio entre caracteres vecinos: "FerÁNdez" machea con "Fernández"
	:: Una letra equívoca: "FernOndez" machea con "Fernández"

Además hay definidas otras operaciones internas que son de menor importancia.


# Lógica para la detección de nombres y apellidos: función "anonimizarTexto" del script "anonimizador.py"

Dado un texto INPUT, las operaciones que se hacen son las siguientes:

1) Detectar nombres/apellidos (genéricamente "palabras") de acuerdo con las listas dadas. Consideramos palabras LARGAS si tienen 6 letras o más, y CORTAS en caso complementario
	:: Los matchs de palabras largas se consideran con máxima prioridad de reemplazo (prioridad=0)
	:: Los matchs de palabras cortas se consideran con menor prioridad (prioridad=1)
	:: Los matchs "imprecisos" de palabras largas son la siguiente jerarquía (prioridad=2)
	:: Los matchs "imprecisos" de palabras cortas se descartan

2) Calcular máxima cobertura de reemplazo
	:: Dados los índices de todos los matchs hallados, calculamos la máxima cobertura del string. Por ejemplo supongamos que "Perezoski" y "Pérez" son apellidos. Entonces en el string "JUAN ES PEREZOSKI" se reemplazará en los intervalos "(JUAN) ES (PEREZOSKI)" en lugar de en "(JUAN) ES (PEREZ)OSKI"
	:: Obtenidas todas las coberturas maximales, se elige la de mayor prioridad

3) Tachar baches: las palabras cortas que quedan entre reemplazos se tachan
	:: "Juan Del Valle" se detectan las palabras "(Juan) Del (Valle)", luego "Del" se tacha por ser corta:  "NOMBRE XXX APELLIDO"
