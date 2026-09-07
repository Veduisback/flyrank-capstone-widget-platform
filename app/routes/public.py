import json
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from fastapi.responses import JSONResponse

from app.db import get_connection
from app.schemas import SubmissionRequest
from app.services.rate_limit import ip_limiter, widget_limiter
from app.services.submissions import create_submission
from app.services.widgets import get_public_widget


router = APIRouter(tags=["public"])


@router.get("/widgets/{widget_id}/config")
def widget_config(widget_id: UUID):
    row = get_public_widget(widget_id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    response = JSONResponse(
        {
            "id": str(row[0]),
            "type": row[2],
            "title": row[3],
            "description": row[4],
            "fields": row[5],
            "button_text": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
        }
    )

    response.headers["Cache-Control"] = "public, max-age=60"

    return response

@router.get("/widget.v1.js")
def widget_script():
    script = """
(function () {
    const scriptElement = document.currentScript || document.querySelector('script[src*="widget.v1.js"]');

    const params = new URL(scriptElement.src).searchParams;
    const widgetId = params.get("id");

    if (!widgetId) {
        console.error("Widget ID missing");
        return;
    }

    const apiBase = scriptElement
        ? new URL(scriptElement.src).origin
        : window.location.origin;

    fetch(apiBase + "/widgets/" + widgetId + "/config")
        .then(response => response.json())
        .then(config => {
            const container = document.createElement("div");

            container.style.maxWidth = "420px";
            container.style.padding = "20px";
            container.style.border = "1px solid #ddd";
            container.style.borderRadius = "8px";
            container.style.fontFamily = "Arial";

            const title = document.createElement("h3");
            title.textContent = config.title;
            container.appendChild(title);

            if (config.description) {
                const description = document.createElement("p");
                description.textContent = config.description;
                container.appendChild(description);
            }

            const form = document.createElement("form");

            config.fields.forEach(field => {
                const input = document.createElement("input");

                input.name = field;
                input.placeholder = field;
                input.required = true;

                input.style.display = "block";
                input.style.width = "100%";
                input.style.marginBottom = "10px";
                input.style.padding = "8px";
                input.style.boxSizing = "border-box";

                form.appendChild(input);
            });

            const honeypot = document.createElement("input");
            honeypot.name = "website";
            honeypot.style.display = "none";
            honeypot.tabIndex = -1;
            honeypot.autocomplete = "off";
            form.appendChild(honeypot);

            const button = document.createElement("button");
            button.type = "submit";
            button.textContent = config.button_text;

            form.appendChild(button);

            const message = document.createElement("p");
            form.appendChild(message);

            form.addEventListener("submit", async function (event) {
                event.preventDefault();

                const data = {};

                config.fields.forEach(field => {
                    data[field] = form.elements[field].value;
                });

                data.honeypot = honeypot.value;

                const response = await fetch(
                    apiBase + "/submissions",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            widget_id: widgetId,
                            data: data,
                            honeypot: honeypot.value
                        })
                    }
                );

                if (response.ok) {
                    message.textContent = "Thanks! Your submission was received.";
                    form.reset();
                } else {
                    const error = await response.json();
                    message.textContent =
                        error.detail || "Submission failed.";
                }
            });

            container.appendChild(form);

            if (scriptElement && scriptElement.parentElement) {
                scriptElement.parentElement.appendChild(container);
            } else {
                document.body.appendChild(container);
            }
        });
})();
"""

    response = Response(
        content=script,
        media_type="application/javascript",
    )

    response.headers["Cache-Control"] = (
        "public, max-age=31536000, immutable"
    )

    return response


@router.post("/submissions")
def submit(
    payload: SubmissionRequest,
    request: Request,
):
    client_ip = request.client.host if request.client else "127.0.0.1"

    if not ip_limiter.allow(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )

    try:
        widget_id = UUID(payload.widget_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid widget_id",
        )

    if not widget_limiter.allow(str(widget_id)):
        raise HTTPException(
            status_code=429,
            detail="Widget rate limit exceeded",
        )

    if payload.honeypot:
        return {
            "status": "accepted"
        }

    idempotency_key = request.headers.get(
        "Idempotency-Key"
    )

    try:
        result = create_submission(
            widget_id=widget_id,
            data=payload.data,
            ip_address=client_ip,
            idempotency_key=idempotency_key,
        )
    except Exception as exc:
        print(f"SUBMISSION ERROR: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Submission error: {type(exc).__name__}: {exc}",
        )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return {
        "id": str(result["id"]),
        "status": "accepted",
        "duplicate": result["duplicate"],
        "geo": {
            "country": result.get("country"),
            "city": result.get("city"),
            "provider": result.get("provider"),
        },
    }