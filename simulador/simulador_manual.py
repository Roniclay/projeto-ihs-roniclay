import argparse
import sys
from pathlib import Path

from protocolo import (
    criar_descricao,
    notas_diff,
    validar_nota,
    normalizar_notas,
)

DISPOSITIVO_PADRAO = "/tmp/ihs_projeto_simulado"


def escrever_notas(caminho_dispositivo: str, notas: str) -> None:
    caminho = Path(caminho_dispositivo)

    with caminho.open("w") as dispositivo:
        dispositivo.write(notas + "\n")


def print_help() -> None:
    print("")
    print("Comandos disponiveis:")
    print("  00000 ate 11111  envia uma mascara no formato MAMIP")
    print("  reset            envia 00000")
    print("  show             mostra o ultimo estado")
    print("  help             mostra esta ajuda")
    print("  exit             sai do simulador")
    print("")
    print("Formato MAMIP:")
    print("  posicao 0 = minimo")
    print("  posicao 1 = anelar")
    print("  posicao 2 = medio")
    print("  posicao 3 = indicador")
    print("  posicao 4 = polegar")
    print("")
    print("Regra:")
    print("  0 = dedo levantado")
    print("  1 = dedo abaixado")
    print("")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Simulador manual IHS-GLOVE-PROTO v0.1"
    )

    parser.add_argument(
        "--dispositivo",
        default=DISPOSITIVO_PADRAO,
        help="Caminho do dispositivo ou arquivo de saida",
    )

    args = parser.parse_args()

    caminho_dispositivo = args.dispositivo
    ultima_nota = "00000"

    print("Simulador manual IHS-GLOVE-PROTO v0.1")
    print(f"Destino: {caminho_dispositivo}")
    print("")
    print("Digite uma nota de 5 bits no formato MAMIP.")
    print("Exemplo: 01010")
    print("Digite help para ajuda.")
    print("")

    try:
        escrever_notas(caminho_dispositivo, ultima_nota)
    except PermissionError:
        print(f"Erro: sem permissao para escrever em {caminho_dispositivo}")
        return 1
    except FileNotFoundError:
        print(f"Erro: destino nao encontrado: {caminho_dispositivo}")
        return 1

    while True:
        try:
            entrada_nota = input("MAMIP> ").strip()
        except KeyboardInterrupt:
            print("")
            print("Encerrando simulador.")
            return 0

        if entrada_nota == "":
            continue

        comando = entrada_nota.lower()

        if comando in ("exit", "quit", "sair", "q"):
            print("Encerrando simulador.")
            return 0

        if comando == "help":
            print_help()
            continue

        if comando == "show":
            print("")
            print(criar_descricao(ultima_nota))
            print("")
            continue

        if comando == "reset":
            nova_nota = "00000"
        else:
            nova_nota = normalizar_notas(entrada_nota)

        if not validar_nota(nova_nota):
            print(f"Mascara invalida: {entrada_nota}")
            print("Use exatamente 5 caracteres, apenas com 0 ou 1.")
            print("Exemplo valido: 01010")
            continue

        eventos = notas_diff(ultima_nota, nova_nota)

        try:
            escrever_notas(caminho_dispositivo, nova_nota)
        except PermissionError:
            print(f"Erro: sem permissao para escrever em {caminho_dispositivo}")
            return 1
        except FileNotFoundError:
            print(f"Erro: destino nao encontrado: {caminho_dispositivo}")
            return 1

        print("")
        print(criar_descricao(nova_nota))

        if len(eventos) == 0:
            print("")
            print("Nenhuma mudanca de estado.")
        else:
            print("")
            print("Eventos simulados:")

            for evento in eventos:
                dedo = evento["dedo"]
                tecla = evento["tecla"]
                acao = evento["acao"]

                print(f"  {acao:9s} | {dedo:9s} | {tecla}")

        print("")

        ultima_nota = nova_nota


if __name__ == "__main__":
    sys.exit(main())
