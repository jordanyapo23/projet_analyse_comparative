"""Point d'entrée du projet d'analyse comparative."""

import sys

from controllers.analyse_controller import lancer_application


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    lancer_application()


if __name__ == "__main__":
    main()
