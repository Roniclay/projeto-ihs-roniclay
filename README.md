# Projeto IHS — Luva virtual

Execute todos os comandos abaixo na raiz do projeto.

## 1. Carregar o driver

```bash
./scripts/load_driver.sh
```

Esse comando compila o driver, carrega o módulo no kernel e cria o dispositivo `/dev/ihs_projeto`.

## 2. Executar com a webcam

```bash
./scripts/run_webcam_driver.sh
```

Posicione a mão em frente à webcam. Para encerrar, pressione `q`.

## Teste manual (opcional)

Também é possível enviar um estado diretamente ao driver:

```bash
echo "01010" | sudo tee /dev/ihs_projeto
```

Cada estado possui cinco números no formato `MAMIP` (mínimo, anelar, médio, indicador e polegar):

- `0`: dedo levantado;
- `1`: dedo abaixado.

## 3. Remover o driver

Ao finalizar, execute:

```bash
./scripts/unload_driver.sh
```

