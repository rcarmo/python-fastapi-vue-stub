#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
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
from os import environ
import json
import asyncio
import httpx
import itertools
from .utils import PDFGenerator
from typing import Dict
import uuid

app = FastAPI()
template_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
pdf_generator = PDFGenerator()

# Use a dictionary for managing subscribers
subscribers: Dict[str, asyncio.Queue] = {}

# Enable CORS (for development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to format a string as an SSE message.
def format_sse(data: str, event: str = None) -> str:
    msg = ""
    if event is not None:
        msg += f"event: {event}\n"
    msg += f"data: {data}\n\n"
    return msg

async def broadcast_message(message: str):
    dead_connections = set()
    for connection_id, queue in list(subscribers.items()):
        try:
            await queue.put(message)
        except Exception as e:
            print(f"Error sending to {connection_id}: {e}")
            dead_connections.add(connection_id)
    for connection_id in dead_connections:
        subscribers.pop(connection_id, None)

# Background job: Call an API endpoint every 15 seconds and broadcast with "api" tag.
async def background_api_fetcher():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Use a URL that matches your actual run configuration.
                response = await client.get(f"http://127.0.0.1:{environ.get("PORT","8000")}/actions/some_action")
                response.raise_for_status()
                data = response.json()
                message = format_sse(json.dumps(data), event="api")
                await broadcast_message(message)
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
                message = format_sse(json.dumps({"message": "no data"}), event="database")
            await broadcast_message(message)
        except Exception as e:
            print("Error in background_db_generator:", e)
        await asyncio.sleep(3)

async def send_to_connection(connection_id: str, message: str):
    if connection_id in subscribers:
        try:
            await subscribers[connection_id].put(message)
            return True
        except Exception as e:
            print(f"Error sending to {connection_id}: {e}")
            subscribers.pop(connection_id, None)
    return False

@app.post("/send/{connection_id}")
async def send_to_specific_client(connection_id: str, message: dict):
    if connection_id in subscribers:
        sse_message = format_sse(json.dumps(message), event="specific")
        success = await send_to_connection(connection_id, sse_message)
        return {"success": success}
    return {"success": False, "error": "Connection not found"}

@app.get("/generate-pdf")
async def generate_pdf():
    try:
        engine = connect()
        table_data = list(get_data(engine))[:50]
        pdf_buffer = pdf_generator.generate_order_report(table_data)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=order_report.pdf"}
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# SSE event generator that yields messages from its queue.
async def event_generator():
    connection_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    subscribers[connection_id] = queue
    print(f"New client connected. Total connections: {len(subscribers)}")
    connect_message = format_sse(json.dumps({"connectionId": connection_id}), event="connect")
    yield connect_message
    try:
        while True:
            message = await queue.get()
            yield message
    except asyncio.CancelledError:
        raise
    finally:
        del subscribers[connection_id]
        print(f"Client disconnected. Remaining connections: {len(subscribers)}")

@app.get("/events")
async def events():
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/actions/{action}")
async def actions(action: str):
    return {
        "orderId": "42",
        "orderDate": datetime.now().isoformat(),
        "customerName": "BATMAN",
        "employeeName": "ROBIN"
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
async def startup_event():
    # Optionally add a small delay here if needed
    asyncio.create_task(background_api_fetcher())
    asyncio.create_task(background_db_generator())

if __name__ == "__main__":
    run("stub.app:app", host=environ.get("BIND_ADDRESS", "127.0.0.1"),
        port=int(environ.get("PORT", 8000)), reload=True)
