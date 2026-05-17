from PySide6 import QtWidgets, QtCore


class Sidebar(QtWidgets.QFrame):
    start_requested = QtCore.Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        # Días de simulación
        self.spin_days = QtWidgets.QSpinBox()
        self.spin_days.setRange(1, 3650)
        self.spin_days.setValue(360)
        form.addRow("Días de simulación:", self.spin_days)

        # Iteraciones Monte Carlo
        self.spin_runs = QtWidgets.QSpinBox()
        self.spin_runs.setRange(1, 1000000)
        self.spin_runs.setValue(1000)
        form.addRow("Iteraciones MC:", self.spin_runs)

        # Inversión inicial
        self.spin_initial = QtWidgets.QDoubleSpinBox()
        self.spin_initial.setRange(0.0, 1e9)
        self.spin_initial.setValue(1000.0)
        self.spin_initial.setPrefix("$")
        form.addRow("Inversión inicial:", self.spin_initial)

        # Tasa de descuento anual
        self.spin_discount = QtWidgets.QDoubleSpinBox()
        self.spin_discount.setRange(0.0, 1.0)
        self.spin_discount.setSingleStep(0.005)
        self.spin_discount.setValue(0.05)
        form.addRow("Tasa descuento (anual):", self.spin_discount)

        # Parámetros de distribuciones (sección comprimible)
        params_group = QtWidgets.QGroupBox("Parámetros de distribuciones")
        pg_layout = QtWidgets.QFormLayout()
        # Poisson lambda
        self.spin_lambda = QtWidgets.QDoubleSpinBox()
        self.spin_lambda.setRange(0.0, 100.0)
        self.spin_lambda.setValue(0.8)
        pg_layout.addRow("λ Poisson (nuevas/día):", self.spin_lambda)
        # Erlang mean and var
        self.spin_erlang_mean = QtWidgets.QDoubleSpinBox()
        self.spin_erlang_mean.setRange(0.1, 1e9)
        self.spin_erlang_mean.setValue(1000.0)
        self.spin_erlang_var = QtWidgets.QDoubleSpinBox()
        self.spin_erlang_var.setRange(0.1, 1e12)
        self.spin_erlang_var.setValue(4000.0)
        pg_layout.addRow("Erlang media:", self.spin_erlang_mean)
        pg_layout.addRow("Erlang varianza:", self.spin_erlang_var)
        # Geométrica mean
        self.spin_geom_mean = QtWidgets.QDoubleSpinBox()
        self.spin_geom_mean.setRange(1.0, 10000.0)
        self.spin_geom_mean.setValue(200.0)
        pg_layout.addRow("Geom. media (días):", self.spin_geom_mean)
        # Tasa diaria mean/std
        self.spin_rate_mean = QtWidgets.QDoubleSpinBox()
        self.spin_rate_mean.setDecimals(6)
        self.spin_rate_mean.setRange(-1.0, 1.0)
        self.spin_rate_mean.setValue(0.0008)
        self.spin_rate_std = QtWidgets.QDoubleSpinBox()
        self.spin_rate_std.setDecimals(6)
        self.spin_rate_std.setRange(0.0, 1.0)
        self.spin_rate_std.setValue(0.0009)
        pg_layout.addRow("Tasa diaria media:", self.spin_rate_mean)
        pg_layout.addRow("Tasa diaria std:", self.spin_rate_std)

        params_group.setLayout(pg_layout)

        layout.addLayout(form)
        layout.addWidget(params_group)

        # Botón iniciar
        self.btn_start = QtWidgets.QPushButton("Iniciar simulación")
        self.btn_start.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.btn_start.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_start.setStyleSheet("padding: 10px; font-weight: 600; background-color: #1f6feb; color: #ffffff; border-radius: 8px;")
        layout.addWidget(self.btn_start)

        # Barra de progreso
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Área de logs
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(150)
        layout.addWidget(self.log)

        layout.addStretch()

        # Conexiones
        self.btn_start.clicked.connect(self._on_start_clicked)

    def _on_start_clicked(self) -> None:
        params = {
            "days": int(self.spin_days.value()),
            "n_runs": int(self.spin_runs.value()),
            "initial_amount": float(self.spin_initial.value()),
            "discount_rate": float(self.spin_discount.value()),
            "poisson_lambda": float(self.spin_lambda.value()),
            "erlang_mean": float(self.spin_erlang_mean.value()),
            "erlang_var": float(self.spin_erlang_var.value()),
            "geom_mean": float(self.spin_geom_mean.value()),
            "rate_mean": float(self.spin_rate_mean.value()),
            "rate_std": float(self.spin_rate_std.value()),
        }
        self.start_requested.emit(params)

    def append_log(self, message: str) -> None:
        self.log.append(message)
