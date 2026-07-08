import cv2
import mediapipe as mp


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Erro: nao foi possivel abrir a webcam.")
        return

    mp_maos = mp.solutions.hands
    mp_desenho = mp.solutions.drawing_utils

    detector_maos = mp_maos.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    )

    print("Detector de mao iniciado.")
    print("Pressione q para sair.")

    while True:
        sucesso, frame = camera.read()

        if not sucesso:
            print("Erro: nao foi possivel ler frame.")
            break

        frame = cv2.flip(frame, 1)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado = detector_maos.process(frame_rgb)

        if resultado.multi_hand_landmarks:
            for mao in resultado.multi_hand_landmarks:
                mp_desenho.draw_landmarks(
                    frame,
                    mao,
                    mp_maos.HAND_CONNECTIONS,
                )

        cv2.imshow("Detector de Mao - IHS", frame)

        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("q"):
            break

    detector_maos.close()
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()