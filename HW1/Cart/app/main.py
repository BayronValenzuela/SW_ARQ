from typing import Union
import requests

from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

CATALOG_URL = "http://catalog_service:80"
app = FastAPI()
mongodb_client = MongoClient("cart_service_mongodb", 27017)
db = mongodb_client.cart_service_db

class Product(BaseModel):
    id: int | None = None
    name: str
    price: float

class CartItem(BaseModel):
    product_id: int
    quantity: int

@app.get("/")
def show_cart():
    all_products = [CartItem(**cart_item).dict() for cart_item in db.cart.find()]
    return all_products


@app.get("/total/")
def total() -> float:
    total = 0
    # N + 1
    for item in db.cart.find():
        url = f"{CATALOG_URL}/products/{item['product_id']}"
        product = requests.get(url).json()
        total += product['price'] * item['quantity']
    return total


@app.post("/add_to_cart/")
def add_to_cart(item: CartItem) -> str:
    url = f"{CATALOG_URL}/products/{item.product_id}"
    product = requests.get(url).json()
    if product is None:
        return 'Product does not exist, check the id and try again'
    
    db.cart.insert_one(item.dict())
    return 'Item added to cart'


@app.delete("/delete_cart/")
def delete_cart() -> str:
    db.cart.delete_many({})
    return 'Cart deleted'
