from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from app.utils import crossmint
from solders.keypair import Keypair
from app.stake.actions import create_stake, delegate_stake
from app.stake.constants import MINIMUM_DELEGATION
from solana.rpc.async_api import AsyncClient

create_stake_router = APIRouter()

# Load environment variables
load_dotenv()


async_client = AsyncClient(os.getenv("RPC_ENDPOINT"))


class CreateStakeRequest(BaseModel):
    amount: int
    validator_address: str
    payer: str


@create_stake_router.post("/create_stake")
async def create_new_stake(request: CreateStakeRequest):
    try:
        
        amount = request.amount
        validator_address = request.validator_address
        payer = request.payer


        if amount < MINIMUM_DELEGATION:
            raise HTTPException(status_code=400, detail="Amount must be at least the minimum delegation.")


        stake_keypair = Keypair()
        [create_txn,create_sig] = await create_stake(async_client, payer, stake_keypair, amount)
        fin_create = await crossmint.create_transaction(create_txn)
        delegate_txn = await delegate_stake(async_client, payer, stake_keypair.pubkey(),validator_address)
        fin_delegate = await crossmint.create_transaction(delegate_txn)

        print(fin_create)
        


        return {"message": "Stake created and delegated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
