from fastapi import FastAPI, Request
import httpx
from fastapi.responses import Response

app = FastAPI()

# Định nghĩa các service backend
SERVICE_URLS = {
    "auth": "http://auth_api:8001",
    "session": "http://session_api:8006",
    "billing": "http://billing_api:8002",
    "booking": "http://booking_api:8003",
    "court": "http://manage_court_api:8004",
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICE_URLS:
        return Response(content=f"Service {service} not found", status_code=404)

    url = f"{SERVICE_URLS[service]}/{path}"
    method = request.method
    headers = {key: value for key, value in request.headers.items() if key.lower() != "host"}
    body = await request.body()

    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=headers, content=body, timeout=None)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type")
    )
