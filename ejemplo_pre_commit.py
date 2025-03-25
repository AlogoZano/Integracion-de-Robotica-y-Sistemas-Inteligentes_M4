"""Calculadora cool."""
import json


class Calculadora:
    """Clase realizar operaciones básicas y gestionar el historial."""

    def init(self):
        """Inicializa la calculadora con un historial vacío."""
        self.historial = []

    def sumar(self, a: float, b: float) -> float:
        """Suma dos números y guarda el resultado en el historial.

        Args:
            a (float): Primer número.
            b (float): Segundo número.

        Returns:
            float: Resultado de la suma.
        """
        resultado = a + b
        self.historial.append({"operacion": "suma", "resultado": resultado})
        return resultado

    def restar(self, a: float, b: float) -> float:
        """Resta dos números y guarda el resultado en el historial.

        Args:
            a (float): Minuendo.
            b (float): Sustraendo.

        Returns:
            float: Resultado de la resta.
        """
        resultado = a - b
        self.historial.append({"operacion": "resta", "resultado": resultado})
        return resultado

    def imprimir_historial(self) -> None:
        """Imprime el historial de operaciones realizadas."""
        for entrada in self.historial:
            print(f"{entrada['operacion']}: {entrada['resultado']}")

    def guardar_historial(self, archivo: str) -> None:
        """Guarda el historial de operaciones en un archivo JSON.

        Args:
            archivo (str): Nombre del archivo donde se guardará el historial.
        """
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(self.historial, f, indent=4)


def ejecutar() -> None:
    """Función principal para ejecutar la calculadora."""
    print("Iniciando ejecución")


if __name__ == "__main__":
    ejecutar()
    calc = Calculadora()
    calc.sumar(5, 3)
    calc.restar(10, 2)
    calc.imprimir_historial()
    calc.guardar_historial("historial.json")
