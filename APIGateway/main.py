from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from fastapi.responses import Response
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Định nghĩa các service backend
# QUAN TRỌNG: KHÔNG thêm prefix vào URL vì nginx/gateway đã xử lý
SERVICE_URLS = {
    "auth": "http://auth_service:8001",
    "billing": "http://billing_service:8002",
    "booking": "http://booking_service:8003",
    "court": "http://court_service:8004",
    "facility": "http://facility_service:8005",
    "notification": "http://notification_service:8007",
    "report": "http://report_service:8009",
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICE_URLS:
        logger.error(f"Service not found: {service}")
        return Response(content=f"Service {service} not found", status_code=404)

    # Build full URL - add service prefix for billing service
    if service == "billing":
        # Handle empty path case
        if path:
            url = f"{SERVICE_URLS[service]}/billing/{path}"
        else:
            url = f"{SERVICE_URLS[service]}/billing"
    else:
        url = f"{SERVICE_URLS[service]}/{path}"
    
    method = request.method
    query = str(request.query_params) if request.query_params else ""
    logger.info(f"Proxying {method} {service}/{path}{('?' + query) if query else ''} -> {url}")
    
    headers = {key: value for key, value in request.headers.items() if key.lower() not in ["host", "content-length"]}
    
    # Add ngrok bypass header for external requests
    headers["ngrok-skip-browser-warning"] = "true"
    
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method,
                url,
                headers=headers,
                content=body,
                params=request.query_params,
            )

        # Build response headers
        response_headers = dict(resp.headers)
        response_headers.pop("content-encoding", None)  # Remove to avoid double encoding
        response_headers.pop("transfer-encoding", None)

        logger.info(f"Response: {resp.status_code} from {service}/{path}")

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=response_headers,
            media_type=resp.headers.get("content-type")
        )
    except httpx.TimeoutException as e:
        logger.error(f"Timeout calling {service}/{path}: {str(e)}")
        return Response(
            content=f"Gateway timeout calling {service}",
            status_code=504
        )
    except Exception as e:
        logger.error(f"Error proxying to {service}/{path}: {str(e)}")
        return Response(
            content=f"Gateway error: {str(e)}",
            status_code=502
        )
