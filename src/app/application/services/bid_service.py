from app.application.ports.auction_repository import AuctionRepository
from app.application.ports.bid_repository import BidRepository
from app.api.v1.schemas.bid import BidCreate, BidResponse
from app.domain.enums import AuctionState
from app.domain.models import Bid
from uuid import UUID


class BidService:
    def __init__(self, bid_repository: BidRepository, auction_repository: AuctionRepository, logger):
        self.bid_repository = bid_repository
        self.auction_repository = auction_repository
        self.logger = logger

    
    async def place_bid(self, bid_in: BidCreate, auction_id: UUID, bidder_id: UUID) -> Bid:
        """
        Orquesta el proceso de pujar:
        1. Obtiene la subasta.
        2. Ejecuta la lógica de dominio (validaciones).
        3. Guarda la puja.
        4. Actualiza la subasta (nuevo precio/ganador).
        """
        # 1. Obtener subasta (con sus pujas actuales cargadas, si es posible)
        auction = await self.auction_repository.get_by_id(auction_id)
        if not auction:
            raise ValueError("Subasta no encontrada")
        
        # 2. Lógica de Dominio (Entidad Auction decide si la puja es válida)
        new_bid = auction.place_bid(amount = bid_in.amount, bidder_id = bidder_id)

        # 3. Persistir puja
        saved_bid = await self.bid_repository.create(new_bid)

        # 4. Persistir cambios en subasta (precio y ganador actualizados)
        await self.auction_repository.update(auction)

        return saved_bid
    

    async def get_auction_bids(self, auction_id: UUID) -> list[Bid]:
        """Obtiene el historial de pujas activas."""
        all_bids = await self.bid_repository.get_by_auction_id(auction_id)
        # Filtramos en memoria por si el repositorio devuelve borradas (doble seguridad)
        return [b for b in all_bids if b.deleted_at is None]
    

    async def retract_bid(self, bid_id: UUID, user_id: UUID) -> None:
        """
        Borrado lógico de una puja.
        Si la puja eliminada era la ganadora, recalcula el estado de la subasta.
        """
        # 1. Recuperar la puja.
        bid = await self.bid_repository.get_by_id(bid_id)
        if not bid:
            raise ValueError("Puja no encontrada.")
        
        # 2. Seguridad: ¿Es el dueño de la puja?
        if bid.bidder_id != user_id:
            raise PermissionError("No tienes permiso para retirar esta puja.")
        
        # 3. Recuperar la subasta asociada
        auction = await self.auction_repository.get_by_id(bid.auction_id)

        # Validar: No se pueden retirar pujas si la subasta ya acabó
        if not auction.is_open and auction.state != AuctionState.ACTIVE:
            raise ValueError("No se puede retirar una puja de una subasta finalizada.")
        
        # 4. Ejecutar el borrado lógico
        await self.bid_repository.delete(bid_id)

        # 5. Recalculo el estado.
        # Verifico si la puja borrada era la ganadora actual
        is_winner = (auction.winner_id == bid.bidder_id) and (auction.current_price == bid.amount)

        if is_winner:
            # Necesitamos encontrar al "Segundo Mejor Postor"
            all_bids = await self.bid_repository.get_by_auction_id(auction.id)

            # Filtramos la que acabamos de borrar y cualquier otra borrada y asumimos que el repositorio las devuelve ordenadas por monto DESC
            active_bids = [
                b for b in all_bids
                if b.deleted_at is None and b.id != bid_id
            ]

            if not active_bids:
                # Caso A: No quedan pujas. Volvemos al inicio
                auction.current_price = auction.starting_price
                auction.winner_id = None
            else:
                # Caso B: Hay una segunda puja más alta
                next_best_bid = active_bids[0]
                auction.current_price = next_best_bid.amount
                auction.winner_id = next_best_bid.bidder_id
            
            # Guardamos el nuevo estado corregido de la subasta
            await self.auction_repository.update(auction)
