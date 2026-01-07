from app.api.dependencies.auctions import get_auction_service
from app.api.v1.schemas.auction import AuctionCreate
from app.application.services.auction_service import AuctionService
from app.domain.models.auction import Auction
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID


router = APIRouter(prefix = "/auctions")


@router.post("/", status_code = 201, response_model = Auction) # El 201 es el estándar para 'Created'
async def create_auction(
    auction_in: AuctionCreate,
    service: AuctionService = Depends(get_auction_service)
):
    return await service.create_auction(auction_in)


@router.get("/{auction_id}")
async def get_auction(
    auction_id: UUID,
    service: AuctionService = Depends(get_auction_service)
):
    auction = await service.get_auction(auction_id)
    if not auction:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Subasta no encontrada")
    return auction
