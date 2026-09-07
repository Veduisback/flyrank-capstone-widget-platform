from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.db import get_connection
from app.schemas import WidgetCreate, WidgetUpdate
from app.services.widgets import create_widget, get_widget, update_widget


router = APIRouter(prefix="/widgets", tags=["widgets"])


@router.post("", status_code=201)
def create(
    payload: WidgetCreate,
    current_user=Depends(get_current_user),
):
    widget_id = create_widget(
        current_user["tenant_id"],
        payload,
    )

    return {
        "id": widget_id,
        "snippet": (
            '<script src="http://localhost:8000/widget.v1.js'
            f'?id={widget_id}"></script>'
        ),
    }


@router.get("/{widget_id}")
def read(
    widget_id: UUID,
    current_user=Depends(get_current_user),
):
    row = get_widget(
        
        current_user["tenant_id"],
        widget_id,
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return {
        "id": row[0],
        "tenant_id": row[1],
        "widget_type": row[2],
        "title": row[3],
        "description": row[4],
        "fields": row[5],
        "button_text": row[6],
        "created_at": row[7],
    }

@router.put("/{widget_id}")
def update(
    widget_id: UUID,
    payload: WidgetUpdate,
    current_user=Depends(get_current_user),
):
    row = update_widget(
        current_user["tenant_id"],
        widget_id,
        payload,
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return {
        "id": row[0],
        "tenant_id": row[1],
        "widget_type": row[2],
        "title": row[3],
        "description": row[4],
        "fields": row[5],
        "button_text": row[6],
        "created_at": row[7],
    }
@router.delete("/{widget_id}", status_code=204)
def delete(
    widget_id: UUID,
    current_user=Depends(get_current_user),
):
    with get_connection() as connection:
        result = connection.execute(
            """
            DELETE FROM widgets
            WHERE id = %s
              AND tenant_id = %s
            """,
            (
                widget_id,
                current_user["tenant_id"],
            ),
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Widget not found",
            )