import cv2


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Erro: nao foi possivel abrir a webcam.")
        return

    print("Webcam aberta com sucesso.")
    print("Pressione q para sair.")

    while True:
        sucesso, frame = camera.read()

        if not sucesso:
            print("Erro: nao foi possivel ler frame da webcam.")
            break

        cv2.imshow("Teste Webcam - IHS", frame)

        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()