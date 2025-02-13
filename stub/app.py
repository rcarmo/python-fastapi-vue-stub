#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .models import connect, get_data
from datetime import datetime
from uvicorn import run
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from pathlib import Path
import json
import asyncio
import httpx
import itertools
from .utils import PDFGenerator


app = FastAPI()
template_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
pdf_generator = PDFGenerator()

# Enable CORS (for development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global list of subscribers. Each subscriber is an asyncio.Queue.
subscribers = []


# Helper function to format a string as an SSE message.
def format_sse(data: str, event: str = None) -> str:
    msg = ""
    if event is not None:
        msg += f"event: {event}\n"
    msg += f"data: {data}\n\n"
    return msg

# Background job: Call an API endpoint every 15 seconds and broadcast with "api" tag.
async def background_api_fetcher():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Adjust the URL/endpoint as needed.
                response = await client.get("http://localhost:8000/actions/some_action")
                response.raise_for_status()
                data = response.json()
                print("Background API fetcher received:", data)
                message = format_sse(json.dumps(data), event="api")
                # Broadcast message to all subscribers.
                for queue in subscribers:
                    await queue.put(message)
            except Exception as e:
                print("Error in background_api_fetcher:", e)
            await asyncio.sleep(13)


# Background job: Cycle through database data and broadcast with "database" tag.
async def background_db_generator():
    try:
        engine = connect()
        results = list(get_data(engine))
    except Exception as e:
        print("Error connecting to DB:", e)
        results = []
    # If there are records, cycle repeatedly.
    record_cycle = itertools.cycle(results) if results else None

    while True:
        try:
            if record_cycle:
                order, customer, employee = next(record_cycle)
                payload = {
                    "orderId": order.order_id,
                    "orderDate": order.order_date.isoformat(),
                    "customerName": customer.customer_name,
                    "employeeName": f"{employee.first_name} {employee.last_name}"
                }
                message = format_sse(json.dumps(payload), event="database")
            else:
                # If no records, you can send a heartbeat or skip.
                message = format_sse(json.dumps({"message": "no data"}), event="database")
            # Broadcast message to all subscribers.
            for queue in subscribers:
                await queue.put(message)
        except Exception as e:
            print("Error in background_db_generator:", e)
        await asyncio.sleep(3)



@app.get("/generate-pdf")
async def generate_pdf():
    try:
        engine = connect()
        table_data =  list(get_data(engine))[:50]

        pdf_buffer = pdf_generator.generate_order_report(table_data)

        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=order_report.pdf"
            }
        )

    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SSE event generator that yields messages from its queue.
async def event_generator():
    queue = asyncio.Queue()
    subscribers.append(queue)
    try:
        while True:
            message = await queue.get()
            yield message
    except asyncio.CancelledError:
        raise
    finally:
        subscribers.remove(queue)


# SSE endpoint that streams events to the client.
@app.get("/events")
async def events():
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Action endpoint (dummy) returning JSON data.
@app.get("/actions/{action}")
async def actions(action: str):
    return {
        "orderId": "42",
        "orderDate": datetime.now().isoformat(),
        "customerName": "BATMAN",
        "employeeName": "ROBIN"
    }


# Serve static assets.
app.mount("/", StaticFiles(directory="static", html=True), name="static")


# Startup event: Launch both background jobs.
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_api_fetcher())
    asyncio.create_task(background_db_generator())


if __name__ == "__main__":
    run("stub.app:app", host="127.0.0.1", port=8000, reload=True)
