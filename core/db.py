# core/db.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DB(ABC):
    """
    Abstract database interface for pluggable DB implementations.
    
    Supports basic CRUD operations with:
    - select() - query with filters, ordering, pagination
    - insert() - create new rows
    - update() - modify existing rows
    - delete() - remove rows
    - query() - raw SQL execution (MySQL only)
    """

    @abstractmethod
    def select(
        self,
        tbname: str,
        filters: Optional[Dict[str, Any]] = None,
        *,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Select rows from table.
        
        Args:
            tbname: Table name
            filters: Dictionary of {column: value} for AND equality filters
            order_by: Column name (or "-name" for DESC)
            limit: Limit result count
            offset: Result offset (requires limit)
        
        Returns:
            List of row dictionaries
        """
        pass

    @abstractmethod
    def insert(self, tbname: str, data: Dict[str, Any]) -> int:
        """
        Insert a row and return its ID.
        
        Args:
            tbname: Table name
            data: Dictionary of column: value pairs
        
        Returns:
            The new row's ID
        """
        pass

    @abstractmethod
    def update(self, tbname: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """
        Update rows matching filter.
        
        Args:
            tbname: Table name
            data: Dictionary of columns to update
            where: Filter dictionary for rows to update
        
        Returns:
            Number of rows updated
        """
        pass

    @abstractmethod
    def delete(self, tbname: str, where: Dict[str, Any]) -> int:
        """
        Delete rows matching filter.
        
        Args:
            tbname: Table name
            where: Filter dictionary for rows to delete
        
        Returns:
            Number of rows deleted
        """
        pass

    @abstractmethod
    def query(self, sql: str, params: tuple = ()) -> Any:
        """
        Execute raw SQL query (SELECT/INSERT/UPDATE/DELETE).
        
        Args:
            sql: Raw SQL string
            params: Tuple of parameter values
        
        Returns:
            For SELECT: list of row dictionaries
            For mutations: number of affected rows
        """
        pass

    def execute(self, sql: str, params: tuple = ()) -> Any:
        """
        Alias for query() - execute raw SQL query.
        
        Args:
            sql: Raw SQL string
            params: Tuple of parameter values
        
        Returns:
            For SELECT: list of row dictionaries
            For mutations: number of affected rows
        """
        return self.query(sql, params)
