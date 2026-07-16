# Protocolo IHS-GLOVE-PROTO v0.1

## Objetivo

Este protocolo define como o simulador, a webcam ou os sensores Hall com ímã devem enviar o estado dos dedos para o driver de kernel da luva.

A regra principal do projeto é separar a origem dos dados do driver. Como o projeto pode utilizar diferentes fontes de entrada, a ideia é manter essa camada isolada. Assim, caso algum protótipo não funcione como esperado, será possível substituir a fonte dos dados por outra mais simples sem alterar a lógica principal do driver.

Em resumo, o driver não precisa saber se os dados vieram de um simulador, da webcam ou dos sensores físicos. Ele deve receber apenas uma máscara binária padronizada com o estado dos dedos.

---

## Formato da mensagem

A mensagem possui 5 caracteres, cada um representando um dedo da mão.

Formato:

```text
MAMIP
```

Onde:

```text
M = Mínimo
A = Anelar
M = Médio
I = Indicador
P = Polegar
```

Cada posição deve conter apenas `0` ou `1`.

Ordem dos dedos:

| Posição | Dedo      |
| ------: | --------- |
|       0 | Mínimo    |
|       1 | Anelar    |
|       2 | Médio     |
|       3 | Indicador |
|       4 | Polegar   |

---

## Significado dos valores

```text
0 = dedo levantado
1 = dedo abaixado
```

---

## Exemplo

Mensagem:

```text
01010
```

Interpretação seguindo o formato `MAMIP`:

| Posição | Dedo      | Valor | Estado    |
| ------: | --------- | ----: | --------- |
|       0 | Mínimo    |     0 | levantado |
|       1 | Anelar    |     1 | abaixado  |
|       2 | Médio     |     0 | levantado |
|       3 | Indicador |     1 | abaixado  |
|       4 | Polegar   |     0 | levantado |

Portanto, a mensagem `01010` significa que os dedos **Anelar** e **Indicador** estão abaixados.

---

## Mensagens válidas

Exemplos:

```text
00000
10000
01000
00100
00010
00001
11111
01010
```

Interpretação de alguns exemplos:

| Mensagem | Interpretação               |
| -------- | --------------------------- |
| `00000`  | Todos os dedos levantados   |
| `10000`  | Apenas o Mínimo abaixado    |
| `01000`  | Apenas o Anelar abaixado    |
| `00100`  | Apenas o Médio abaixado     |
| `00010`  | Apenas o Indicador abaixado |
| `00001`  | Apenas o Polegar abaixado   |
| `11111`  | Todos os dedos abaixados    |

---

## Mensagens inválidas

Exemplos:

```text
abcde
12345
010
010101
0000a
```

O driver deve rejeitar qualquer mensagem que não possua exatamente 5 posições binárias.

Ou seja, a mensagem deve ter:

```text
5 caracteres
apenas 0 ou 1
```

---

## Device de comunicação

O driver de kernel deverá criar o seguinte character device:

```text
/dev/ihs_projeto
```

Os programas em user space deverão escrever a máscara nesse device.

Exemplo de teste manual:

```bash
echo "01010" | sudo tee /dev/ihs_projeto
```

Esse comando envia a máscara `01010` para o driver. Seguindo o protocolo `MAMIP`, isso indica que os dedos **Anelar** e **Indicador** estão abaixados.

---

## Mapeamento inicial de teclas

O mapeamento inicial dos dedos para teclas será:

| Posição | Dedo      | Tecla Linux |
| ------: | --------- | ----------- |
|       0 | Mínimo    | KEY_A       |
|       1 | Anelar    | KEY_S       |
|       2 | Médio     | KEY_J       |
|       3 | Indicador | KEY_K       |
|       4 | Polegar   | KEY_SPACE   |

Assim, cada dedo abaixado representa uma tecla virtual enviada pelo driver ao sistema operacional.

---

## Regra de evento

O driver deve comparar o estado atual com o estado anterior.

Se uma posição mudar de `0` para `1`, o driver deve pressionar a tecla correspondente.

Se uma posição mudar de `1` para `0`, o driver deve soltar a tecla correspondente.

Essa regra evita que o driver envie a mesma tecla repetidamente enquanto o dedo permanece abaixado.

---

## Exemplo de mudança de estado

Estado anterior:

```text
00000
```

Novo estado:

```text
01000
```

Interpretação:

```text
O dedo Anelar mudou de levantado para abaixado.
```

Resultado esperado no driver:

```text
Pressionar KEY_S
```

---

## Exemplo de soltura de tecla

Estado anterior:

```text
01000
```

Novo estado:

```text
00000
```

Interpretação:

```text
O dedo Anelar mudou de abaixado para levantado.
```

Resultado esperado no driver:

```text
Soltar KEY_S
```

---

## Exemplo com múltiplos dedos

Estado anterior:

```text
00000
```

Novo estado:

```text
01010
```

Interpretação:

| Dedo      | Mudança              |
| --------- | -------------------- |
| Anelar    | levantado → abaixado |
| Indicador | levantado → abaixado |

Resultado esperado no driver:

```text
Pressionar KEY_S
Pressionar KEY_K
```

Depois, se o novo estado for:

```text
00000
```

Resultado esperado:

```text
Soltar KEY_S
Soltar KEY_K
```

---

