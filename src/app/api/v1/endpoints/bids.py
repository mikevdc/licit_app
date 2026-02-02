from app.api.dependencies.bids import get_bid_service
from app.api.dependencies.auth import get_current_user
from app.api.v1.schemas.bid import BidCreate, BidResponse
from app.application.services.bid_service import BidService
from app.domain.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated
from uuid import UUID

router = APIRouter(prefix = "/bids")

ServiceDep = Annotated[BidService, Depends(get_bid_service)]
CurrentUserDep = Annotated[User, get_current_user]

@router.post("/", response_model = BidResponse, status_code = 201)
async def place_bid(
    bid_in: BidCreate,
    current_user: CurrentUserDep,
    service: ServiceDep
):
    try:
        return await service.place_bid(
            bid_in = bid_in,
            auction_id = bid_in.auction_id,
            bidder_id = current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))


@router.get("/auction/{auction_id}", response_model = list[BidResponse])
async def list_auction_bids(
    auction_id: UUID,
    service: ServiceDep
):
    return await service.get_auction_bids(auction_id)


@router.delete("/{bid_id}", status_code = 204)
async def retract_bid(
    bid_id: UUID,
    current_user: CurrentUserDep,
    service: ServiceDep
):
    try:
        await service.retract_bid(bid_id, user_id = current_user.id)
    except PermissionError:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "No puedes retirar esta puja.")
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))
