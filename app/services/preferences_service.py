from uuid import UUID
from typing import Optional
from app.models.preferences import NotificationPreferences, PreferencesUpdateRequest
from app.repositories.preferences_repository import get_preferences_by_user, update_preferences


def fetch_user_preferences(tenant_id: str, user_id: UUID) -> Optional[NotificationPreferences]:
    return get_preferences_by_user(tenant_id, user_id)


def apply_preference_updates(
    tenant_id: str,
    user_id: UUID,
    request: PreferencesUpdateRequest,
    version: str,
) -> Optional[NotificationPreferences]:
    updates = request.model_dump(exclude_none=True)
    return update_preferences(tenant_id, user_id, version, updates)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user_id