from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class HotelPrice(Base):
    __tablename__ = 'HotelPrice'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    Hotel = Column(String, nullable=False)
    Price = Column(Float, nullable=False)
    Review = Column(Float, nullable=False)
    Location = Column(String, nullable=False)
    PriceReview = Column('Price/Review', Float, nullable=False)
    City = Column(String, nullable=False)
    Date = Column(String, nullable=False)
    AsOf = Column(TIMESTAMP, nullable=False)


class AverageRoomPriceByDate(Base):
    __tablename__ = 'AverageRoomPriceByDateTable'

    Date = Column(String, primary_key=True)
    AveragePrice = Column(Float, nullable=False)
    City = Column(String, nullable=False)


class AverageHotelRoomPriceByReview(Base):
    __tablename__ = 'AverageHotelRoomPriceByReview'

    Review = Column(Float, primary_key=True)
    AveragePrice = Column(Float, nullable=False)


class AverageHotelRoomPriceByDayOfWeek(Base):
    __tablename__ = 'AverageHotelRoomPriceByDayOfWeek'

    DayOfWeek = Column(String, primary_key=True)
    AveragePrice = Column(Float, nullable=False)


class AverageHotelRoomPriceByMonth(Base):
    __tablename__ = 'AverageHotelRoomPriceByMonth'

    Month = Column(String, primary_key=True)
    AveragePrice = Column(Float, nullable=False)
    Quarter = Column(String, nullable=False)


class AverageHotelRoomPriceByLocation(Base):
    __tablename__ = 'AverageHotelRoomPriceByLocation'

    Location = Column(String, primary_key=True)
    AveragePrice = Column(Float, nullable=False)
    AverageRating = Column(Float, nullable=False)
    AveragePricePerReview = Column(Float, nullable=False)


class JapanHotel(Base):
    __tablename__ = 'JapanHotels'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    Hotel = Column(String, nullable=False)
    Price = Column(Float, nullable=False)
    Review = Column(Float, nullable=False)
    PriceReview = Column('Price/Review', Float, nullable=False)
    Date = Column(String, nullable=False)
    Region = Column(String, nullable=False)
    Prefecture = Column(String, nullable=False)
    Location = Column(String, nullable=False)
    AsOf = Column(TIMESTAMP, nullable=False)
