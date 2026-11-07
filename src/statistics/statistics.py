import sqlite3
from ..fill_db import DB_PATH
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPdfWriter, QPageLayout, QPageSize
from PyQt6.QtCharts import (
    QChart, QChartView, QPieSeries, QLineSeries, 
    QDateTimeAxis, QValueAxis, QCategoryAxis
)


