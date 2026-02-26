from PyQt6.QtWidgets import QFrame


class CardFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")
        self.setProperty("cardSelected", "false")

    def set_selected(self, selected: bool) -> None:
        self.setProperty("cardSelected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
