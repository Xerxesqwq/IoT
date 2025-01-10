from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, select, ForeignKey, DateTime, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool
from dataclasses import dataclass
from contextlib import contextmanager
import asyncio
import json

class Base(DeclarativeBase):
    pass

class Device(Base):
    __tablename__ = "Devices"
    
    device_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    device_type: Mapped[Optional[str]] = mapped_column(String(255))
    
    # 关系定义
    events: Mapped[List["Event"]] = relationship("Event", back_populates="device")

class Event(Base):
    __tablename__ = "Events"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("Devices.device_id"))
    event_time: Mapped[datetime] = mapped_column(DateTime)
    data: Mapped[Optional[str]] = mapped_column(String(255))
    
    # 关系定义
    device: Mapped[Device] = relationship("Device", back_populates="events")

class User(Base):
    __tablename__ = "User"
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))


class DatabaseManager:
    def __init__(self, sync_mode: bool = True):
        self.sync_mode = sync_mode
        
        if sync_mode:
            # 同步引擎
            self.engine = create_engine(
                "mysql+mysqlconnector://IoT:P+SsHJDgDN4ktA==@10.119.13.108:3306/Design",
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False
            )
        else:
            # 异步引擎
            self.engine = create_async_engine(
                "mysql+asyncmy://IoT:P+SsHJDgDN4ktA==@10.119.13.108:3306/Design",
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False
            )

    @contextmanager
    def get_session(self):
        """同步会话上下文管理器"""
        if not self.sync_mode:
            raise RuntimeError("Please use async_session for async mode")
        
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def async_session(self):
        """异步会话上下文管理器"""
        if self.sync_mode:
            raise RuntimeError("Please use get_session for sync mode")
        
        async with AsyncSession(self.engine) as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # 设备相关方法 - 同步版本
    def add_device(self, name: str, user_id: int, device_type: str) -> int:
        with self.get_session() as session:
            device = Device(name=name, user_id=user_id, device_type=device_type)
            session.add(device)
            session.commit()
            return device.device_id

    def get_device(self, device_id: int) -> Optional[Device]:
        with self.get_session() as session:
            return session.get(Device, device_id)

    def get_device_id(self, user_id: int, name: str) -> Optional[int]:
        with self.get_session() as session:
            stmt = select(Device.device_id).where(Device.user_id == user_id, Device.name == name)
            result = session.execute(stmt).scalar_one_or_none()
            if result is not None:
                return result
            return -1
    
    def get_device_status(self, id: int, name = ""):
        if name == "":
            device_id = id
        else:
            device_id = self.get_device_id(id, name)
        with self.get_session() as session:
            device_type = session.execute(select(Device.device_type).where(Device.device_id == device_id)).scalar_one_or_none()
            # status: the latest status of the device, query from event table
            # select data from Events where device_id = device_id order by event_time desc limit 1
            stmt = select(Event.data).where(Event.device_id == device_id).order_by(Event.event_time.desc()).limit(1)
            status = session.execute(stmt).scalar_one_or_none()
            data = {"device_id": device_id}
            data["status"] = status
            data["device_type"] = device_type
            
        if data.get("status") is None:
            return None
        return data
    #Device Status, return a json
    # LED: status: ON/OFF
    
    def get_user_devices(self, user_id: int) -> List[Device]:
        with self.get_session() as session:
            stmt = select(Device.device_id).where(Device.user_id == user_id).order_by(Device.device_id)
            return list(session.execute(stmt).scalars())

    def get_user_devices_by_type(self, user_id: int, device_type: str) -> List[Device]:
        with self.get_session() as session:
            stmt = select(Device.name).where(Device.user_id == user_id, Device.device_type == device_type)
            # return a list of device_ids
            return list(session.execute(stmt).scalars())
    
    def update_device(self, device_id: int, **kwargs) -> bool:
        with self.get_session() as session:
            device = session.get(Device, device_id)
            if not device:
                return False
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            return True

    def delete_device(self, device_id: int) -> bool:
        with self.get_session() as session:
            device = session.get(Device, device_id)
            if not device:
                return False
            session.delete(device)
            return True

    def user_login(self, username: str, password: str) -> Optional[int]:
        with self.get_session() as session:
            stmt = select(User.user_id).where(User.username == username, User.password == password)
            result = session.execute(stmt).scalar_one_or_none()
            if result is not None:
                return result
            return -1
        
    def get_all_device_status(self, user_id: int):
        """
        Get all devices status of a user, return a json
        """
        device_list = self.get_user_devices(user_id)
        status_list = []
        for each in device_list:
            _status = self.get_device_status(each)
            status_list.append(_status)
        return status_list
    
    # 设备相关方法 - 异步版本
    async def async_add_device(self, name: str, user_id: int, device_type: str) -> int:
        async with self.async_session() as session:
            device = Device(name=name, user_id=user_id, device_type=device_type)
            session.add(device)
            await session.commit()
            return device.device_id

    async def async_get_device(self, device_id: int) -> Optional[Device]:
        async with self.async_session() as session:
            return await session.get(Device, device_id)

    # 事件相关方法 - 同步版本
    def log_event(self, device_id: int, data: str, event_time: Optional[datetime] = None):
        if event_time is None:
            event_time = datetime.now()
            
        with self.get_session() as session:
            event = Event(device_id=device_id, event_time=event_time, data=data)
            session.add(event)

    def get_device_events(
        self, 
        device_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Event]:
        with self.get_session() as session:
            stmt = select(Event).where(Event.device_id == device_id)
            
            if start_time:
                stmt = stmt.where(Event.event_time >= start_time)
            if end_time:
                stmt = stmt.where(Event.event_time <= end_time)
                
            stmt = stmt.order_by(Event.event_time.desc())
            return list(session.execute(stmt).scalars())

    # 事件相关方法 - 异步版本
    async def async_log_event(
        self, 
        device_id: int, 
        data: str, 
        event_time: Optional[datetime] = None
    ):
        if event_time is None:
            event_time = datetime.now()
            
        async with self.async_session() as session:
            event = Event(device_id=device_id, event_time=event_time, data=data)
            session.add(event)
            await session.commit()

    # 通用查询方法
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Any]:
        with self.get_session() as session:
            result = session.execute(query, params or {})
            return list(result)

    async def async_execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Any]:
        async with self.async_session() as session:
            result = await session.execute(query, params or {})
            return list(result)