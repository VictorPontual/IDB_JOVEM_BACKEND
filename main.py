from pydantic import BaseModel
from fastapi import FastAPI, status

app = FastAPI()


class EventCreate(BaseModel):
    title: str
    date: str
    location: str
    description: str | None = None
    capacity: int | None = None


@app.get("/")
def read_root():
    return {"message": "IDB Jovem Backend está rodando!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate):
    return {
        "id": 1,
        "title": event.title,
        "date": event.date,
        "location": event.location,
        "description": event.description,
        "capacity": event.capacity,
    }