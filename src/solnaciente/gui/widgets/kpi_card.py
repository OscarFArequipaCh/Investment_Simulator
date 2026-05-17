from PySide6 import QtGui, QtWidgets


class KpiCard(QtWidgets.QFrame):
    def __init__(self, title: str, icon: QtGui.QIcon | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setObjectName("kpiCard")
        self.setStyleSheet(
            "#kpiCard { border-radius: 14px; background-color: #32383f; padding: 16px; }"
        )
        self._build_ui(title, icon)

    def _build_ui(self, title: str, icon: QtGui.QIcon | None) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)

        header = QtWidgets.QHBoxLayout()
        self.label_title = QtWidgets.QLabel(title)
        self.label_title.setStyleSheet("color: #a6b0bf; font-size: 12px; font-weight: 600;")
        header.addWidget(self.label_title)
        header.addStretch()

        if icon is not None:
            icon_label = QtWidgets.QLabel()
            icon_label.setPixmap(icon.pixmap(20, 20))
            header.addWidget(icon_label)

        self.value_label = QtWidgets.QLabel("0")
        self.value_label.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: 700;")
        self.value_label.setMinimumHeight(40)

        self.trend_label = QtWidgets.QLabel("")
        self.trend_label.setStyleSheet("color: #8fbd7a; font-size: 11px;")

        layout.addLayout(header)
        layout.addWidget(self.value_label)
        layout.addWidget(self.trend_label)

    def set_value(self, value: str, subtext: str = "", positive: bool = True) -> None:
        self.value_label.setText(value)
        arrow = "▲" if positive else "▼"
        color = "#8fbd7a" if positive else "#f26c6c"
        self.trend_label.setText(f"{arrow} {subtext}")
        self.trend_label.setStyleSheet(f"color: {color}; font-size: 11px;")
