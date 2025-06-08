from fastapi import FastAPI
from domain.post import post_router
from domain.user import user_router
from domain.crew import crew_router
from domain.match import match_router
app = FastAPI()

app.include_router(user_router.router)
app.include_router(crew_router.router)
app.include_router(post_router.router)
app.include_router(match_router.router)