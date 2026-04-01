"""Configuración pytest para tests del backend"""
import sys
import os

# Agregar backend/ al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
