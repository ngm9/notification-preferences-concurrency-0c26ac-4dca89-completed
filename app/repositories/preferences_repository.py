from uuid import UUID
from typing import Optional
from app.database import get_db
from app.models.preferences import NotificationPreferences


def get_preferences_by_user(tenant_id:str, user_id: UUID) -> Optional[NotificationPreferences]:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, tenant_id, email_enabled, sms_enabled, push_enabled, frequency, version "
                "FROM notification_preferences WHERE user_id = %s and tenant_id = %s",
                (str(user_id), str(tenant_id)),
            )
            row = cur.fetchone()
            if not row:
                return None
            return NotificationPreferences(**row)


def update_preferences(tenant_id:str, user_id: UUID, expected_version:str, updates: dict) -> Optional[NotificationPreferences]:
    if not updates:
        return get_preferences_by_user(tenant_id, user_id)

    set_clauses = ", ".join(f"{key} = %s" for key in updates)
    values = list(updates.values())

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE notification_preferences SET {set_clauses}, updated_at = NOW(), version = version + 1 "
                f"WHERE user_id = %s and tenant_id = %s and version = %s"
                f"RETURNING user_id, tenant_id, email_enabled, sms_enabled, push_enabled, frequency, version",
                values + [str(user_id)], str(tenant_id), str(expected_version),
            )
            row = cur.fetchone()
            if not row:
                return None
            if row.rowcount == 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "VERSION_CONFLICT",
                        "message": "Record was modified by another request. Refresh and retry."
                    }
                )

            return NotificationPreferences(**row)
