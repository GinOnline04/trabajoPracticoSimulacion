import sys

sys.dont_write_bytecode = True

from src.vacunatorio.ui.interfaz import Aplicacion


if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
