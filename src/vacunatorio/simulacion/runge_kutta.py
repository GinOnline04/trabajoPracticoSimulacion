from src.vacunatorio.config.constantes import COEFICIENTE_RK_DERECHO, COEFICIENTE_RK_IZQUIERDO


def derivada_r(_t, r):
    return (COEFICIENTE_RK_IZQUIERDO - COEFICIENTE_RK_DERECHO) * r


def calcular_runge_kutta(parametros):
    """
    Resuelve por RK4:
        41,4 * R = dR/dt + 0,0575 * R

    Despeje:
        dR/dt = (41,4 - 0,0575) * R

    El tiempo de vencimiento se toma como el valor maximo de R dentro del
    intervalo calculado. El enunciado fija la ecuacion; por eso sus
    coeficientes no son editables en la interfaz.
    """
    filas = []
    t = parametros.rk_t_inicial
    r = parametros.rk_r_inicial
    h = parametros.rk_paso
    maximo = r
    indice = 0

    while t <= parametros.rk_t_final + 1e-12 and indice < 10000:
        k1 = h * derivada_r(t, r)
        k2 = h * derivada_r(t + h / 2, r + k1 / 2)
        k3 = h * derivada_r(t + h / 2, r + k2 / 2)
        k4 = h * derivada_r(t + h, r + k3)
        r_siguiente = r + (k1 + 2 * k2 + 2 * k3 + k4) / 6

        filas.append(
            {
                "i": indice,
                "t": t,
                "R": r,
                "k1": k1,
                "k2": k2,
                "k3": k3,
                "k4": k4,
                "R siguiente": r_siguiente,
            }
        )

        maximo = max(maximo, r)
        t += h
        r = r_siguiente
        indice += 1

    maximo = max(maximo, r)
    return filas, maximo
