from solders.pubkey import Pubkey
from solders.keypair import Keypair
import solders.system_program as sys
from solana.constants import SYSTEM_PROGRAM_ID
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solders.sysvar import CLOCK, STAKE_HISTORY
from solders.transaction import Transaction
from solders.message import Message
from solders.hash import Hash
import base58

from app.stake.constants import STAKE_LEN, STAKE_PROGRAM_ID, SYSVAR_STAKE_CONFIG_ID
from app.stake.state import Authorized, Lockup, StakeAuthorize
import app.stake.instructions as st


OPTS = TxOpts(skip_confirmation=False, preflight_commitment=Confirmed)


async def create_stake(client: AsyncClient, payer: str, stake: Keypair,lamports: int):
    print(f"Creating stake {stake.pubkey()}")
    resp = await client.get_minimum_balance_for_rent_exemption(STAKE_LEN)
    instructions = []

    
    ix1 = sys.create_account(
            sys.CreateAccountParams(
                from_pubkey=Pubkey.from_string(payer),
                to_pubkey=stake.pubkey(),
                lamports=resp.value + lamports,
                space=STAKE_LEN,
                owner=STAKE_PROGRAM_ID,
            )
        )
    
    
    ix2 = st.initialize(
            st.InitializeParams(
                stake=stake.pubkey(),
                authorized=Authorized(
                    staker=Pubkey.from_string(payer),
                    withdrawer=Pubkey.from_string(payer),
                ),
                lockup=Lockup(
                    unix_timestamp=0,
                    epoch=0,
                    custodian=SYSTEM_PROGRAM_ID,
                )
            )
        )
    
    instructions.append(ix1)
    instructions.append(ix2)
    
    message = Message.new_with_blockhash(
        instructions,
        Pubkey.from_string("11111111111111111111111111111112"),
        Hash.from_string("11111111111111111111111111111111")
    )
    transaction = Transaction.new_unsigned(message)
    
    serialized_transaction = bytes(transaction)
    serialized_transaction_str = base58.b58encode(serialized_transaction).decode('ascii')

    recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
    transaction.partial_sign([stake],recent_blockhash)

    signed_serialized_transaction = bytes(transaction)
    signed_serialized_transaction_str = base58.b58encode(signed_serialized_transaction).decode('ascii')

    return [serialized_transaction_str,signed_serialized_transaction_str]


async def delegate_stake(client: AsyncClient, payer: str, stake: Pubkey, vote: str):
    print("start delegation")
    instructions = []
    ix= st.delegate_stake(
            st.DelegateStakeParams(
                stake=stake,
                vote=Pubkey.from_string(vote),
                clock_sysvar=CLOCK,
                stake_history_sysvar=STAKE_HISTORY,
                stake_config_id=SYSVAR_STAKE_CONFIG_ID,
                staker=Pubkey.from_string(payer),
            )
        )
    instructions.append(ix)
    message = Message.new_with_blockhash(
        instructions,
        Pubkey.from_string("11111111111111111111111111111112"),
        Hash.from_string("11111111111111111111111111111111")
    )
    transaction = Transaction.new_unsigned(message)

    serialized_transaction = bytes(transaction)
    serialized_transaction_str = base58.b58encode(serialized_transaction).decode('ascii')
    return serialized_transaction_str

    
    


async def authorize(
    client: AsyncClient, payer: Keypair, authority: Keypair, stake: Pubkey,
    new_authority: Pubkey, stake_authorize: StakeAuthorize
):
    txn = Transaction(fee_payer=payer.pubkey())
    txn.add(
        st.authorize(
            st.AuthorizeParams(
                stake=stake,
                clock_sysvar=CLOCK,
                authority=authority.pubkey(),
                new_authority=new_authority,
                stake_authorize=stake_authorize,
            )
        )
    )
    signers = [payer, authority] if payer.pubkey() != authority.pubkey() else [payer]
    recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
    await client.send_transaction(txn, *signers, recent_blockhash=recent_blockhash, opts=OPTS)
