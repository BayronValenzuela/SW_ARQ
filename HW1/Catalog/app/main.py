from typing import Union, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()
mongodb_client = MongoClient("catalog_service_mongodb", 27017)
db = mongodb_client.catalog_service_db

class Product(BaseModel):
    id: int | None = None
    name: str
    price: float


@app.get("/")
def get_all() -> List[dict]:
    all_products = [Product(**product).dict() for product in db.products.find()]
    return all_products


@app.get("/products/{product_id}")
def read_item(product_id: int) -> Union[dict, HTTPException]:
    product = db.products.find_one({"id": product_id}, {"_id": 0})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@app.post("/products/")
def create_products(products: List[Product]) -> str:
    products_dicts = [product.dict() for product in products]
    db.products.insert_many(products_dicts)
    return 'Products created'


@app.delete("/products/")
def delete_all() -> str:
    db.products.delete_many({})
    return 'All products deleted'


@app.delete("/products/{product_id}")
def delete_product(product_id: int) -> str:
    result = db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return 'Product deleted'
