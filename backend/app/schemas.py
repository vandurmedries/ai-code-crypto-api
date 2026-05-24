from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    balance: float
    total_earned: float
    total_spent: float
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class EarningBase(BaseModel):
    amount: float
    source: str
    description: Optional[str] = None


class EarningCreate(EarningBase):
    pass


class Earning(EarningBase):
    id: int
    user_id: int
    confidence_score: Optional[float]
    meta_data: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseBase(BaseModel):
    product_id: str
    product_name: str
    amount: float


class PurchaseCreate(PurchaseBase):
    pass


class Purchase(PurchaseBase):
    id: int
    user_id: int
    status: str
    stripe_payment_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MLModelBase(BaseModel):
    name: str
    model_type: str
    version: str


class MLModelCreate(MLModelBase):
    pass


class MLModel(MLModelBase):
    id: int
    accuracy: Optional[float]
    is_active: bool
    model_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MLPredictionBase(BaseModel):
    prediction_type: str
    confidence: float
    predicted_value: Dict[str, Any]


class MLPredictionCreate(MLPredictionBase):
    pass


class MLPrediction(MLPredictionBase):
    id: int
    user_id: int
    model_id: int
    actual_value: Optional[Dict[str, Any]]
    was_correct: Optional[bool]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarketDataScrape(BaseModel):
    url: str
    source: str
    data_type: str


class EarningOpportunity(BaseModel):
    opportunity_id: str
    type: str
    potential_earning: float
    confidence: float
    description: str
    action_required: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class DashboardStats(BaseModel):
    balance: float
    total_earned: float
    total_spent: float
    recent_earnings: List[Earning]
    recent_purchases: List[Purchase]
    active_opportunities: List[EarningOpportunity]


# Wallet Schemas
class WalletBase(BaseModel):
    currency: str
    network: str
    address: str


class WalletCreate(WalletBase):
    pass


class Wallet(WalletBase):
    id: int
    user_id: int
    balance: float
    pending_balance: float
    wallet_type: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WalletTransactionBase(BaseModel):
    tx_type: str
    amount: float
    currency: str


class WalletTransactionCreate(WalletTransactionBase):
    pass


class WalletTransaction(WalletTransactionBase):
    id: int
    wallet_id: int
    user_id: int
    tx_hash: Optional[str]
    from_address: Optional[str]
    to_address: Optional[str]
    status: str
    confirmations: int
    meta_data: Optional[Dict[str, Any]]
    created_at: datetime
    confirmed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
