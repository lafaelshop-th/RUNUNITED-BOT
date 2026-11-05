from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(BigInteger, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    credits = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)
    is_developer = Column(Boolean, default=False)
    free_trial_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    boards = relationship("Board", back_populates="owner")
    purchases = relationship("Purchase", back_populates="user")

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    guild_id = Column(BigInteger, index=True)
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger, nullable=True)
    verify_message_link = Column(String, nullable=True)
    title = Column(String, default="ร้านค้า")
    description = Column(Text, default="")
    image_url = Column(String, nullable=True)
    contacts = Column(JSON, default=list)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", back_populates="boards")
    products = relationship("Product", back_populates="board")
    settings = relationship("BoardSettings", back_populates="board", uselist=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"))
    name = Column(String)
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer, default=0)
    category = Column(String)  # id_game, rental, code_file
    image_url = Column(String, nullable=True)
    delivery_data = Column(JSON)  # username, password, extra, codes, files, duration_days
    require_platform = Column(Boolean, default=False)
    board = relationship("Board", back_populates="products")

class Code(Base):
    __tablename__ = "codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    reward_type = Column(String)  # role, credit, product, file
    reward_data = Column(JSON)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=True)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    board_id = Column(Integer, ForeignKey("boards.id"))
    amount = Column(Float)
    delivery_sent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="purchases")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # topup, purchase, package
    amount = Column(Float)
    status = Column(String, default="pending")  # pending, approved, rejected
    reference = Column(String, unique=True, nullable=True)
    slip_url = Column(String, nullable=True)
    method = Column(String)  # truemoney, promptpay
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    days = Column(Integer)
    price = Column(Float)
    is_trial = Column(Boolean, default=False)

class BoardSettings(Base):
    __tablename__ = "board_settings"
    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), unique=True)
    truemoney_phone = Column(String, nullable=True)
    promptpay_id = Column(String, nullable=True)
    webhook_url = Column(String, nullable=True)
    board = relationship("Board", back_populates="settings")

class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    guild_id = Column(BigInteger)
    guild_name = Column(String)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    last_ping = Column(Float, default=0.0)
    last_error = Column(Text, nullable=True)
