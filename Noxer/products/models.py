from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ProductTagAssociation(Base):
    __tablename__ = 'product_tag_association'

    product_id: Mapped[int] = mapped_column(ForeignKey(
        'products.id', ondelete="CASCADE"
    ), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey(
        'tags.id',
        ondelete="CASCADE"
    ), primary_key=True)

class ProductCategoryAssociation(Base):
    __tablename__ = 'product_category_association'

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            'products.id',
            ondelete="CASCADE"
        ), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            'categories.id',
            ondelete="CASCADE"
        ),
        primary_key=True
    )

class ProductMarkAssociation(Base):
    __tablename__ = 'product_mark_association'

    product_id: Mapped[int] = mapped_column(ForeignKey(
        'products.id',
        ondelete="CASCADE"
    ), primary_key=True)
    mark_id: Mapped[int] = mapped_column(ForeignKey(
        'product_marks.id',
        ondelete="CASCADE"
    ), primary_key=True)


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    products: Mapped[list["Product"]] = relationship(
        secondary="product_tag_association",
        back_populates="tags",
        uselist=True,
    )


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_url: Mapped[str]
    name: Mapped[str]
    sort_order: Mapped[int | None]

    products: Mapped[list["Product"]] = relationship(
        secondary="product_category_association",
        back_populates="categories",
        uselist=True
    )

class ProductMark(Base):
    __tablename__ = 'product_marks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    products: Mapped[list["Product"]] = relationship(
        secondary="product_mark_association",
        back_populates="marks",
        uselist=True
    )

class Color(Base):
    __tablename__ = 'colors'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(50))
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    discount: Mapped[int | None]
    json_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int | None]

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        back_populates="colors",
        uselist=False
    )

class Extra(Base):
    __tablename__ = 'extras'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    characteristics: Mapped[str] = mapped_column(Text)
    delivery: Mapped[str] = mapped_column(Text)
    kit: Mapped[str] = mapped_column(Text)
    offer: Mapped[str] = mapped_column(Text)
    ai_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        back_populates="extras",
        uselist=False
    )

class Image(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_url: Mapped[str]
    main_image: Mapped[bool]
    position: Mapped[str | None]
    sort_order: Mapped[int | None]
    title: Mapped[str | None]

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        back_populates="images",
        uselist=False,
    )

class Parameter(Base):
    __tablename__ = 'parameters'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chosen: Mapped[bool]
    disabled: Mapped[bool]
    extra_field_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    extra_field_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    old_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    parameter_string: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    sort_order: Mapped[int | None]

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        back_populates="parameters",
        uselist=False
    )

class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_url: Mapped[str]
    sort_order: Mapped[int | None]

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        back_populates="reviews",
        uselist=False
    )

class ReviewVideo(Base):
    __tablename__ = 'review_videos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    poster_url: Mapped[str | None]
    video_url: Mapped[str | None]
    sort_order: Mapped[int | None]

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        back_populates="reviews_video",
        uselist=False
    )

class ExcludedItem(Base):
    __tablename__ = 'excluded_items'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    color_id: Mapped[int | None]
    parameter_id: Mapped[int | None]

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        back_populates="excluded",
        uselist=False
    )

class ImportanceNum(Base):
    __tablename__ = 'importance_nums'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    importance: Mapped[int | None]

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        back_populates="importance_num",
        uselist=False
    )

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    on_main: Mapped[bool]
    name: Mapped[str]
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    moysklad_connector_products_data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    categories: Mapped[list["Category"]] = relationship(
        secondary="product_category_association",
        back_populates="products",
        uselist=True,
    )
    colors: Mapped[list["Color"]] = relationship(
        back_populates="product",
        uselist=True,
        cascade='all, delete-orphan'
    )
    excluded: Mapped[list["ExcludedItem"]] = relationship(
        back_populates="product",
        uselist=True,
        cascade='all, delete-orphan'
    )
    extras: Mapped[list["Extra"]] = relationship(
        back_populates="product",
        uselist=True,
        cascade='all, delete-orphan'
    )
    images: Mapped[list["Image"]] = relationship(
        back_populates="product",
        uselist=True,
        cascade='all, delete-orphan'
    )
    importance_num: Mapped[list["ImportanceNum"]] = relationship(
        back_populates="product",
        uselist=True,
        cascade='all, delete-orphan'
    )
    marks: Mapped[list["ProductMark"]] = relationship(
        secondary="product_mark_association",
        back_populates="products",
        uselist=True,
    )
    parameters: Mapped[list["Parameter"]] = relationship(
        back_populates="product",
        uselist=True,
        cascade='all, delete-orphan'
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="product",
        uselist=True,
        cascade='all, delete-orphan'
    )
    reviews_video: Mapped[list["ReviewVideo"]] = relationship(
        back_populates="product",
        uselist=True,
        cascade='all, delete-orphan'
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="product_tag_association",
        back_populates="products",
        uselist=True,
    )
