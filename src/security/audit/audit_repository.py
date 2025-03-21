from datetime import datetime

from sqlalchemy import BinaryExpression, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.strategy_options import Load

from src.core.repository import BaseRepository
from src.security.models import AuditActionLog


class AuditRepository(BaseRepository[AuditActionLog]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(AuditActionLog, db)

    @staticmethod
    def get_audit_action_log_fields() -> tuple:
        return (
            AuditActionLog.id,
            AuditActionLog.user_id,
            AuditActionLog.endpoint_name,
            AuditActionLog.action,
            AuditActionLog.path_params,
            AuditActionLog.query_params,
            AuditActionLog.request_data,
            AuditActionLog.response_data,
            AuditActionLog.status_code,
            AuditActionLog.ip,
            AuditActionLog.at,
        )

    @staticmethod
    def include_action_data_logs() -> list[Load]:
        base_options = [joinedload(AuditActionLog.audit_data_logs)]

        return base_options

    def get_load_options(
        self,
        include_action_data_logs: bool = False,
    ) -> list[Load]:
        options: list[Load] = []

        if include_action_data_logs:
            options.extend(self.include_action_data_logs())

        return options

    async def find_audit_action_logs(
        self,
        user_ids: list[int] = None,
        actions: list[str] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        limit: int = None,
        offset: int = None,
        apply_unique: bool = False,
        joins: list[tuple] = None,
    ) -> list[AuditActionLog]:
        base_filter: list[BinaryExpression] = []
        options: list[Load] = [] if options is None else options
        joins: list[tuple] = [] if joins is None else joins

        if user_ids:
            base_filter.append(AuditActionLog.user_id.in_(user_ids))

        if actions:
            base_filter.append(AuditActionLog.action.in_(actions))

        if start_date:
            base_filter.append(AuditActionLog.at >= start_date)

        if end_date:
            base_filter.append(AuditActionLog.at <= end_date)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        options.extend(self.get_load_options())

        return await self.find_all(
            filter=filter,
            options=options,
            apply_unique=apply_unique,
            joins=joins,
            limit=limit,
            offset=offset,
            order_by=AuditActionLog.at.desc(),
        )

    async def find_audit_action_log_by_id(
        self,
        audit_action_log_id: str,
        include_action_data_logs: bool = False,
        filter: BinaryExpression = None,
        options: list[Load] = None,
        joins: list[tuple] = None,
    ) -> AuditActionLog | None:
        base_filter: list[BinaryExpression] = []
        options: list[Load] = [] if options is None else options
        joins: list[tuple] = [] if joins is None else joins

        base_filter.append(AuditActionLog.id == audit_action_log_id)

        filter = (
            and_(filter, *base_filter) if filter is not None else and_(*base_filter)
        )

        options.extend(
            self.get_load_options(include_action_data_logs=include_action_data_logs)
        )

        return await self.find(
            filter=filter,
            options=options,
            joins=joins,
        )
