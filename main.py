from fastapi import FastAPI
from domain.post import post_router
from domain.user import user_router

app = FastAPI()

@app.get("/")
def print_hello():
    return "hello"

app.include_router(user_router.router)
app.include_router(post_router.router)