from datetime import UTC, datetime

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    TypeAdapter,
    field_validator,
)

http_url_ta: TypeAdapter = TypeAdapter(HttpUrl)


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True
    )

    @field_validator(
        'image_url',
        'extra_field_image',
        'poster_url',
        'video_url',
        mode='before',
        check_fields=False
    )
    def parse_url(cls, value):
        if isinstance(value, str):
            http_url_ta.validate_python(value)
        return value


class Category(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Category_ID', 'id'))
    image_url: str = Field(
        validation_alias=AliasChoices('Category_Image', 'image_url'),
    )
    name: str = Field(validation_alias=AliasChoices('Category_Name', 'name'))
    sort_order: int | None

class ProductMark(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Mark_ID', 'id'))
    name: str = Field(validation_alias=AliasChoices('Mark_Name', 'name'))

class Color(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Color_ID', 'id'))
    code: str = Field(validation_alias=AliasChoices('Color_Code', 'code'))
    name: str = Field(validation_alias=AliasChoices('Color_Name', 'color'))
    image_url: str | None = Field(
        validation_alias=AliasChoices('Color_image', 'image_url')
    )
    product_id: int = Field(validation_alias=AliasChoices('Product_ID', 'product_id'))
    discount: int | None
    json_data: str | None
    sort_order: int | None

class Extra(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Product_Extra_ID', 'id'))
    product_id: int = Field(validation_alias=AliasChoices( 'Product_ID', 'product_id'))
    characteristics: str = Field(
        validation_alias=AliasChoices('Characteristics', 'characteristics')
    )
    delivery: str = Field(validation_alias=AliasChoices('Delivery', 'delivery'))
    kit: str = Field(validation_alias=AliasChoices('Kit', 'kit'))
    offer: str = Field(validation_alias=AliasChoices('Offer', 'offer'))
    ai_description: str | None

class Image(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Image_ID', 'id'))
    image_url: str = Field(validation_alias=AliasChoices('Image_URL', 'image_url'))
    main_image: bool = Field(validation_alias=AliasChoices('MainImage', 'main_image'))
    product_id: int = Field(validation_alias=AliasChoices('Product_ID', 'product_id'))
    position: str | None
    sort_order: int | None
    title: str | None

class Parameter(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Parameter_ID', 'id'))
    chosen: bool
    disabled: bool
    extra_field_color: str | None
    extra_field_image: str | str | None
    name: str
    old_price: int | None
    parameter_string: str
    price: int
    sort_order: int | None

class Review(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Photo_ID', 'id'))
    image_url: str = Field(validation_alias=AliasChoices('Photo_URL', 'image_url'))
    product_id: int = Field(validation_alias=AliasChoices('Product_ID', 'product_id'))
    sort_order: int | None

class ReviewVideo(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Video_ID', 'id'))
    poster_url: str | None = Field(
        validation_alias=AliasChoices('Poster_URL', 'poster_url')
    )
    product_id: int = Field(validation_alias=AliasChoices('Product_ID', 'product_id'))
    video_url: str = Field(validation_alias=AliasChoices('Video_URL', 'video_url'))
    sort_order: int | None

class ExcludedItem(ORMBaseModel):
    id: int | None
    color_id: int | None
    parameter_id: int | None
    product_id: int | None

class ImportanceNum(ORMBaseModel):
    id: int | None
    importance: int | None
    product_id: int | None

class Tags(ORMBaseModel):
    id: int
    name: str

class Product(ORMBaseModel):
    id: int = Field(validation_alias=AliasChoices('Product_ID', 'id'))
    created_at: datetime = Field(
        validation_alias=AliasChoices('Created_At', 'created_at')
    )
    on_main: bool = Field(validation_alias=AliasChoices('OnMain', 'on_main'))
    name: str = Field(validation_alias=AliasChoices('Product_Name', 'name'))
    updated_at: datetime | None = Field(
        validation_alias=AliasChoices('Updated_At', 'updated_at')
    )
    categories: list[Category]
    colors: list[Color]
    excluded: list[ExcludedItem]
    extras: list[Extra]
    images: list[Image]
    importance_num: list[ImportanceNum] | None
    marks: list[ProductMark]
    moysklad_connector_products_data: str | None
    parameters: list[Parameter]
    reviews: list[Review]
    reviews_video: list[ReviewVideo]
    tags: list[str] | None


    @field_validator('created_at', 'updated_at', mode='before')
    def parse_dates(cls, value):
        if isinstance(value, str):
            dt = datetime.strptime(value, '%a, %d %b %Y %H:%M:%S GMT')
            return dt.replace(tzinfo=UTC)
        return value

class ProductView(Product):
    tags: list[Tags]

class OnlyProductsList(ORMBaseModel):
    products: list[Product]

class RootModel(OnlyProductsList):
    status: str

class OnMainRootModel(RootModel):
    categories: list[Category]
    product_marks: list[ProductMark]
