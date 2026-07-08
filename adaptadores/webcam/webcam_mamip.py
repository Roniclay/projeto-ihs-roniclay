import argparse
import math
import time
from pathlib import Path

import cv2
import mediapipe as mp


DISPOSITIVO_PADRAO = "/tmp/ihs_projeto_simulado"


DEDOS = [
    "minimo",
    "anelar",
    "medio",
    "indicador",
    "polegar",
]


PONTOS_DEDOS = {
    "minimo": (17, 18, 20),
    "anelar": (13, 14, 16),
    "medio": (9, 10, 12),
    "indicador": (5, 6, 8),
    "polegar": (2, 3, 4),
}


def calcular_angulo(ponto_a, ponto_b, ponto_c) -> float:
    """
    Calcula o angulo formado por tres pontos.

    O ponto_b e o ponto central da articulacao.

    Exemplo:
        A = base do dedo
        B = junta do dedo
        C = ponta do dedo

    Quando o dedo esta esticado, o angulo tende a ficar alto,
    perto de 170 ou 180 graus.

    Quando o dedo esta dobrado, o angulo diminui.
    """
    vetor_ba_x = ponto_a.x - ponto_b.x
    vetor_ba_y = ponto_a.y - ponto_b.y

    vetor_bc_x = ponto_c.x - ponto_b.x
    vetor_bc_y = ponto_c.y - ponto_b.y

    produto_escalar = (vetor_ba_x * vetor_bc_x) + (vetor_ba_y * vetor_bc_y)

    tamanho_ba = math.sqrt((vetor_ba_x ** 2) + (vetor_ba_y ** 2))
    tamanho_bc = math.sqrt((vetor_bc_x ** 2) + (vetor_bc_y ** 2))

    if tamanho_ba == 0 or tamanho_bc == 0:
        return 180.0

    cosseno = produto_escalar / (tamanho_ba * tamanho_bc)

    cosseno = max(-1.0, min(1.0, cosseno))

    angulo = math.degrees(math.acos(cosseno))

    return angulo


def atualizar_estado_dedo(
    estado_atual: bool,
    angulo: float,
    limiar_abaixar: float,
    limiar_levantar: float,
) -> bool:
    """
    Aplica histerese.

    Se o dedo esta levantado, ele so vira abaixado quando o angulo
    ficar menor que limiar_abaixar.

    Se o dedo esta abaixado, ele so vira levantado quando o angulo
    ficar maior que limiar_levantar.
    """
    if not estado_atual:
        if angulo < limiar_abaixar:
            return True

        return False

    if angulo > limiar_levantar:
        return False

    return True


def gerar_mamip_por_flexao(
    landmarks,
    estados_dedos: dict,
    limiar_abaixar: float,
    limiar_levantar: float,
    ignorar_polegar: bool,
) -> tuple[str, dict]:
    """
    Gera a nota MAMIP usando angulo real de flexao dos dedos.

    MAMIP:
        posicao 0 = minimo
        posicao 1 = anelar
        posicao 2 = medio
        posicao 3 = indicador
        posicao 4 = polegar

    0 = dedo levantado
    1 = dedo abaixado
    """
    angulos = {}

    for dedo in DEDOS:
        if dedo == "polegar" and ignorar_polegar:
            estados_dedos[dedo] = False
            angulos[dedo] = 180.0
            continue

        ponto_base_id, ponto_junta_id, ponto_ponta_id = PONTOS_DEDOS[dedo]

        ponto_base = landmarks[ponto_base_id]
        ponto_junta = landmarks[ponto_junta_id]
        ponto_ponta = landmarks[ponto_ponta_id]

        angulo = calcular_angulo(ponto_base, ponto_junta, ponto_ponta)

        angulos[dedo] = angulo

        estados_dedos[dedo] = atualizar_estado_dedo(
            estado_atual=estados_dedos[dedo],
            angulo=angulo,
            limiar_abaixar=limiar_abaixar,
            limiar_levantar=limiar_levantar,
        )

    nota = ""

    for dedo in DEDOS:
        nota += "1" if estados_dedos[dedo] else "0"

    return nota, angulos


def escrever_nota(caminho_dispositivo: str, nota: str) -> None:
    caminho = Path(caminho_dispositivo)

    with caminho.open("w") as dispositivo:
        dispositivo.write(nota + "\n")


def desenhar_texto(frame, texto: str, linha: int, escala: float = 0.7) -> None:
    y = 35 + (linha * 30)

    cv2.putText(
        frame,
        texto,
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        escala,
        (0, 255, 0),
        2,
    )


def desenhar_status(frame, nota_bruta: str, nota_estavel: str, angulos: dict) -> None:
    desenhar_texto(frame, f"MAMIP estavel: {nota_estavel}", 0, 0.9)
    desenhar_texto(frame, f"MAMIP bruto:   {nota_bruta}", 1, 0.8)
    desenhar_texto(frame, "MAMIP = minimo anelar medio indicador polegar", 2, 0.6)
    desenhar_texto(frame, "0=levantado | 1=abaixado | q=sair", 3, 0.6)

    linha = 5

    for dedo in DEDOS:
        if dedo in angulos:
            desenhar_texto(frame, f"{dedo}: {angulos[dedo]:.1f} graus", linha, 0.55)
            linha += 1


def main():
    parser = argparse.ArgumentParser(
        description="Adaptador webcam MAMIP com deteccao por flexao real dos dedos"
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Indice da camera. Padrao: 0",
    )

    parser.add_argument(
        "--dispositivo",
        default=DISPOSITIVO_PADRAO,
        help="Arquivo ou device que recebera a nota MAMIP",
    )

    parser.add_argument(
        "--enviar",
        action="store_true",
        help="Envia a nota para o dispositivo informado",
    )

    parser.add_argument(
        "--frames-estaveis",
        type=int,
        default=4,
        help="Quantidade de frames iguais antes de aceitar a nota",
    )

    parser.add_argument(
        "--limiar-abaixar",
        type=float,
        default=135.0,
        help="Angulo maximo para considerar dedo realmente abaixado",
    )

    parser.add_argument(
        "--limiar-levantar",
        type=float,
        default=155.0,
        help="Angulo minimo para considerar dedo realmente levantado",
    )

    parser.add_argument(
        "--ignorar-polegar",
        action="store_true",
        help="Forca o polegar como levantado para reduzir falsos positivos",
    )

    args = parser.parse_args()

    camera = cv2.VideoCapture(args.camera)

    if not camera.isOpened():
        print("Erro: nao foi possivel abrir a webcam.")
        return

    mp_maos = mp.solutions.hands
    mp_desenho = mp.solutions.drawing_utils

    detector_maos = mp_maos.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75,
    )

    estados_dedos = {
        "minimo": False,
        "anelar": False,
        "medio": False,
        "indicador": False,
        "polegar": False,
    }

    nota_estavel = "00000"
    nota_enviada = "00000"
    nota_candidata = None
    contador_candidata = 0

    print("Adaptador webcam MAMIP iniciado.")
    print("Modo: deteccao por flexao real dos dedos")
    print(f"Camera: {args.camera}")
    print(f"Dispositivo destino: {args.dispositivo}")
    print(f"Enviar para dispositivo: {args.enviar}")
    print(f"Frames estaveis: {args.frames_estaveis}")
    print(f"Limiar abaixar: {args.limiar_abaixar}")
    print(f"Limiar levantar: {args.limiar_levantar}")
    print(f"Ignorar polegar: {args.ignorar_polegar}")
    print("Pressione q na janela da webcam para sair.")
    print("")

    if args.enviar:
        try:
            escrever_nota(args.dispositivo, nota_enviada)
        except Exception as erro:
            print(f"Erro ao escrever nota inicial: {erro}")
            return

    while True:
        sucesso, frame = camera.read()

        if not sucesso:
            print("Erro: nao foi possivel ler frame da webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        resultado = detector_maos.process(frame_rgb)

        nota_bruta = "00000"
        angulos = {}

        if resultado.multi_hand_landmarks:
            mao = resultado.multi_hand_landmarks[0]
            landmarks = mao.landmark

            nota_bruta, angulos = gerar_mamip_por_flexao(
                landmarks=landmarks,
                estados_dedos=estados_dedos,
                limiar_abaixar=args.limiar_abaixar,
                limiar_levantar=args.limiar_levantar,
                ignorar_polegar=args.ignorar_polegar,
            )

            mp_desenho.draw_landmarks(
                frame,
                mao,
                mp_maos.HAND_CONNECTIONS,
            )
        else:
            for dedo in estados_dedos:
                estados_dedos[dedo] = False

            nota_bruta = "00000"

        if nota_bruta == nota_candidata:
            contador_candidata += 1
        else:
            nota_candidata = nota_bruta
            contador_candidata = 1

        if contador_candidata >= args.frames_estaveis and nota_candidata != nota_estavel:
            nota_estavel = nota_candidata

            print(f"MAMIP estavel={nota_estavel}")

            if args.enviar and nota_estavel != nota_enviada:
                try:
                    escrever_nota(args.dispositivo, nota_estavel)
                    nota_enviada = nota_estavel
                except PermissionError:
                    print(f"Erro: sem permissao para escrever em {args.dispositivo}")
                    break
                except FileNotFoundError:
                    print(f"Erro: dispositivo nao encontrado: {args.dispositivo}")
                    break

        desenhar_status(frame, nota_bruta, nota_estavel, angulos)

        cv2.imshow("Webcam MAMIP - IHS", frame)

        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("q"):
            break

        time.sleep(0.01)

    if args.enviar:
        try:
            escrever_nota(args.dispositivo, "00000")
        except Exception:
            pass

    detector_maos.close()
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()