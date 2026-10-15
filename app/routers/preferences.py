from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.middleware.auth import decode_token
from app.models.auth import TokenClaims
from app.models.preferences import PreferencesUpdateRequest, PreferencesResponse
from app.services.preferences_service import fetch_user_preferences, apply_preference_updates
import getpass

router = APIRouter()


@router.get("/tenants/{tenant_id}/users/{user_id}/preferences", response_model=PreferencesResponse)
def get_preferences(
    tenant_id: str,
    user_id: UUID,
    claims: TokenClaims = Depends(decode_token),
):

    current_user = get_current_user(decode_token)
    if tenant_id != current_user["tenant_id"]:
        raise HTTPException(
            status_code=403,
            detail="Cross-tenant access denied"
        )
    if current_user!=user_id:
        raise PermissionError("Invalid user")
    prefs = fetch_user_preferences(tenant_id, user_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return PreferencesResponse(**prefs.model_dump())


@router.put("/tenants/{tenant_id}/users/{user_id}/preferences", response_model=PreferencesResponse)
def update_preferences(
    tenant_id: str,
    user_id: UUID,
    body: PreferencesUpdateRequest,
    claims: TokenClaims = Depends(decode_token),
):
    current_user = get_current_user(decode_token)
    if tenant_id != current_user["tenant_id"]:
         raise HTTPException(
        status_code=403,
        detail={
            "code": "CROSS_TENANT_ACCESS_DENIED",
            "message": "You cannot access data belonging to another tenant."
        }
    )
    if current_user!=user_id:
         raise HTTPException(
        status_code=403,
        detail={
            "code": "INVALID_USER",
            "message": "You cannot access data belonging to another user."
        }
    )
    prefs = fetch_user_preferences(tenant_id, user_id)
    updated = apply_preference_updates(tenant_id, user_id, body, pref["version"])
    if not updated:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return PreferencesResponse(**updated.model_dump())


