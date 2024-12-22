from fastapi  import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.create_stake import create_stake_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "This is Sola AI wallet service"}

app.include_router(create_stake_router, prefix="/stake", tags=["stake"])







