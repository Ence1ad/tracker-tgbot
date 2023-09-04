from sqlalchemy import String, ForeignKey, BigInteger, UniqueConstraint, CheckConstraint

from sqlalchemy.orm import Mapped, mapped_column

from db.base_model import SqlAlchemyBase
from settings import LENGTH_NAME_LIMIT


class CategoriesModel(SqlAlchemyBase):
    __tablename__ = 'categories'
    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(LENGTH_NAME_LIMIT), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id', ondelete='cascade'), nullable=False)
    # user = relationship("UserModel", back_populates='categories', lazy='joined')
    # trackers: Mapped["TrackerModel"] = relationship("TrackerModel", back_populates='categories', lazy='joined')
    __table_args__ = (
        UniqueConstraint(user_id, category_name),
        CheckConstraint(sqltext="Length(category_name) > 0")
    )
