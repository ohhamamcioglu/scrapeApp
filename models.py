from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CompetitorData(BaseModel):
    price: Optional[float]
    formattedPrice: Optional[str]
    url: Optional[str]
    image: Optional[str]
    size: Optional[str]

class ProductItem(BaseModel):
    id: str
    name: Optional[str]
    dimension: Optional[str]
    br: Optional[CompetitorData]
    rd: Optional[CompetitorData]
    deb: Optional[CompetitorData]
    lr: Optional[CompetitorData]
    inc: Optional[CompetitorData]
    Lowest_Competitor_GBP: Optional[float]
    Competitor_Name: Optional[str]
    Price_Difference_GBP: Optional[float]
    Price_Difference_Percent: Optional[float]
    margin_gbp: Optional[float] = None
    margin_percent: Optional[float] = None

class PriceHistoryItem(BaseModel):
    timestamp: datetime
    br_price: Optional[float]
    lowest_competitor: Optional[float]
    competitor_name: Optional[str]
    rd_price: Optional[float]
    deb_price: Optional[float]
    lr_price: Optional[float]
    margin_percent: Optional[float] = None

class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[ProductItem]

class ScrapeResponse(BaseModel):
    message: str
