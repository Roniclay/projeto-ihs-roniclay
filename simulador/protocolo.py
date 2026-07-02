ORDEM_DEDOS = [
    "minimo",
    "anelar",
    "medio",
    "indicador",
    "polegar",
]

MAPEAMENTO = {
    "minimo": "KEY_A",
    "anelar": "KEY_S",
    "medio": "KEY_J",
    "indicador": "KEY_K",
    "polegar": "KEY_SPACE",
}


def normalizar_notas(notas: str) -> str:
    nota = notas.strip()

    if nota.startswith("NOTAS="):
        nota = nota.replace("NOTAS=", "", 1).strip()

    if nota.startswith("MASK="):
        nota = nota.replace("MASK=", "", 1).strip()

    return nota


def validar_nota(notas: str) -> bool:
    notas = normalizar_notas(notas)

    if len(notas) != 5:
        return False

    for nota in notas:
        if nota not in ("0", "1"):
            return False

    return True


def analisar_notas(notas: str) -> dict:
    notas = normalizar_notas(notas)

    if not validar_nota(notas):
        raise ValueError(f"Mascara invalida: {notas}")

    resultado = {}

    for i, dedo in enumerate(ORDEM_DEDOS):
        resultado[dedo] = notas[i] == "1"

    return resultado


def criar_descricao(notas: str) -> str:
    notas = normalizar_notas(notas)
    dedos = analisar_notas(notas)

    linhas = []

    linhas.append(f"NOTAS={notas}")
    linhas.append("Formato: MAMIP")
    linhas.append("")

    for i, dedo in enumerate(ORDEM_DEDOS):
        abaixado = dedos[dedo]
        estado = "abaixado" if abaixado else "levantado"
        tecla = MAPEAMENTO[dedo]

        linhas.append(f"posicao {i} | {dedo:9s} | {estado:9s} | {tecla}")

    return "\n".join(linhas)


def notas_diff(nota_antiga: str, nova_nota: str) -> list:
    nota_antiga = normalizar_notas(nota_antiga)
    nova_nota = normalizar_notas(nova_nota)

    if not validar_nota(nota_antiga):
        raise ValueError("Nota anterior invalida")

    if not validar_nota(nova_nota):
        raise ValueError("Nota nova invalida")

    eventos = []

    for i, dedo in enumerate(ORDEM_DEDOS):
        valor_antigo = nota_antiga[i]
        valor_novo = nova_nota[i]

        if valor_antigo == valor_novo:
            continue

        tecla = MAPEAMENTO[dedo]

        if valor_antigo == "0" and valor_novo == "1":
            acao = "PRESSIONE"
        else:
            acao = "SOLTE"

        eventos.append({
            "dedo": dedo,
            "tecla": tecla,
            "acao": acao,
            "posicao": i,
        })

    return eventos


if __name__ == "__main__":
    notas = [
        "00000",
        "10000",
        "01000",
        "00100",
        "00010",
        "00001",
        "11111",
        "01010",
    ]

    for nota in notas:
        print("=" * 70)
        print(criar_descricao(nota))

    print("=" * 70)
    print("Diferenca entre notas:")
    print(notas_diff("00000", "01010"))
