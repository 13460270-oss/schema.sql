from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import os

app = FastAPI(title="Clothing E-Commerce API")

# 開放跨域存取 (CORS) 供前端 Dashboard 連線
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 從環境變數讀取資料庫連線
DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DB_URL,
    connect_args={"ssl": {"ca": "/etc/ssl/certs/ca-certificates.crt"}} if DB_URL and "tidbcloud" in DB_URL else {}
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Clothing API Active"}

@app.get("/api/products")
def get_products(category_id: int = Query(None), limit: int = 60):
    """ 取得 60 件服飾資料與對應圖片 URL """
    try:
        with engine.connect() as conn:
            query = """
                SELECT p.product_id, p.product_name, p.price, p.stock, 
                       p.image_url, c.category_name, c.category_code 
                FROM products p
                JOIN categories c ON p.category_id = c.category_id
            """
            if category_id:
                query += f" WHERE p.category_id = {int(category_id)}"
            query += f" LIMIT {int(limit)}"
            
            result = conn.execute(text(query)).mappings().all()
            return {"success": True, "count": len(result), "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
