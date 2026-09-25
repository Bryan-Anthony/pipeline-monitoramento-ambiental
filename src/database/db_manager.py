import os
from contextlib import contextmanager
from typing import Iterator

import pyodbc


class DatabaseManager:
	"""Gerencia conexoes com o SQL Server do pipeline."""

	def __init__(self, connection_string: str | None = None):
		self.connection_string = connection_string or self._build_connection_string()

	@staticmethod
	def _build_connection_string() -> str:
		configured_connection_string = os.getenv("DB_CONNECTION_STRING")
		if configured_connection_string:
			return configured_connection_string

		driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
		server = os.getenv("DB_SERVER", "localhost")
		database = os.getenv("DB_NAME", "walter")
		trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "yes").lower()

		connection_parts = [
			f"DRIVER={{{driver}}}",
			f"SERVER={server}",
			f"DATABASE={database}",
			"TrustServerCertificate=yes",
		]

		if trusted_connection in {"yes", "true", "1"}:
			connection_parts.append("Trusted_Connection=yes")
		else:
			username = os.getenv("DB_USER")
			password = os.getenv("DB_PASSWORD")
			if not username or not password:
				raise ValueError(
					"Defina DB_USER e DB_PASSWORD para usar autenticacao SQL."
				)
			connection_parts.extend([f"UID={username}", f"PWD={password}"])

		return ";".join(connection_parts)

	def connect(self) -> pyodbc.Connection:
		"""Abre e retorna uma conexao com o banco de dados."""
		return pyodbc.connect(self.connection_string)

	@contextmanager
	def connection(self) -> Iterator[pyodbc.Connection]:
		"""Fornece uma conexao e controla commit, rollback e fechamento."""
		connection = self.connect()
		try:
			yield connection
			connection.commit()
		except Exception:
			connection.rollback()
			raise
		finally:
			connection.close()
