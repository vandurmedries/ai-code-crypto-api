from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import hashlib


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    balance = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    
    earnings = relationship("Earning", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")
    ml_predictions = relationship("MLPrediction", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")
    wallet_transactions = relationship("WalletTransaction", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")
    wallet_transactions = relationship("WalletTransaction", back_populates="user")


class Earning(Base):
    __tablename__ = "earnings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    source = Column(String, nullable=False)  # 'ai_prediction', 'affiliate', 'data_analysis'
    description = Column(Text)
    confidence_score = Column(Float)  # AI confidence in this earning opportunity
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="earnings")


class Purchase(Base):
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, completed, failed, refunded
    stripe_payment_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="purchases")


class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # 'earnings_predictor', 'market_analyzer', 'user_behavior'
    version = Column(String, nullable=False)
    accuracy = Column(Float)
    is_active = Column(Boolean, default=True)
    model_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MLPrediction(Base):
    __tablename__ = "ml_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=False)
    prediction_type = Column(String, nullable=False)  # 'earning_opportunity', 'market_trend', 'user_interest'
    confidence = Column(Float, nullable=False)
    predicted_value = Column(JSON)
    actual_value = Column(JSON)
    was_correct = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="ml_predictions")
    model = relationship("MLModel")


class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # 'trends', 'prices', 'sentiment'
    content = Column(JSON)
    raw_html = Column(Text)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    is_processed = Column(Boolean, default=False)


class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Blockchain info
    currency = Column(String, nullable=False)  # 'BTC', 'ETH', 'SOL', 'USDT'
    network = Column(String, nullable=False)  # 'mainnet', 'testnet'
    
    # Wallet addresses
    address = Column(String, nullable=False)  # Public address for deposits
    private_key_encrypted = Column(String)  # Encrypted private key (for managed wallets)
    
    # Balance tracking
    balance = Column(Float, default=0.0)  # On-chain balance
    pending_balance = Column(Float, default=0.0)  # Pending deposits
    
    # Wallet type
    wallet_type = Column(String, default="platform")  # 'platform', 'external', 'connected'
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="wallets")
    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Transaction details
    tx_type = Column(String, nullable=False)  # 'deposit', 'withdrawal', 'internal'
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    
    # Blockchain tx info
    tx_hash = Column(String)  # On-chain transaction hash
    from_address = Column(String)
    to_address = Column(String)
    
    # Status
    status = Column(String, default="pending")  # 'pending', 'confirmed', 'failed'
    confirmations = Column(Integer, default=0)
    
    # Meta
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    
    wallet = relationship("Wallet", back_populates="transactions")
    user = relationship("User", back_populates="wallet_transactions")
