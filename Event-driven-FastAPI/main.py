import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(  # type: ignore
    host="redis-17712.c300.eu-central-1-1.ec2.cloud.redislabs.com",
    port=17712,
    password="yFbs7ZxLr8z74OkrAE3A7DG87QVerPFG",
    decode_responses=True,
)


class Delivery(HashModel):
    budget: int = 0
    notes: str = ""

    class Meta:
        database = redis


class Event(HashModel):
    delivery_id: str = ""
    type: str
    data: str

    class Meta:
        database = redis


@app.post("/deliveries/create")
async def create(request: Request):
    body = await request.json()
    delivery = Delivery(
        budget=body["data"]["budget"], notes=body["data"]["notes"]
    ).save()
    event = Event(
        delivery_id=delivery.pk, type=body['type'], data=json.dumps(body['data'])
    )
    return event
