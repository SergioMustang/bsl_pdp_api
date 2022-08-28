import datetime as dt
import typing as tp

from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from db.base import Base

ModelType = tp.TypeVar("ModelType", bound=Base)
PydanticModelType = tp.TypeVar("PydanticModelType", bound=BaseModel)


class CRUDBase(tp.Generic[ModelType]):
    def __init__(self, model: tp.Type[ModelType], db: Session):
        self.db = db
        self.model = model

    def get(
        self,
        filters: dict,
    ):
        return self.db.execute(select(self.model).filter_by(**filters)).scalars().first()

    def get_all(
        self,
        filters: dict,
    ):
        return self.db.execute(select(self.model).filter_by(**filters)).scalars().all()

    def create_or_update(
        self,
        obj_update: tp.Generic[PydanticModelType],
        flush: tp.Optional[bool] = None,
    ):
        obj_id = getattr(obj_update, 'id')
        if obj_id is not None:
            obj = self.get(
                {
                    'id': obj_id,
                }
            )
            self.update(
                obj=obj,
                obj_update=obj_update,
            )
        else:
            obj = self.model(**obj_update.dict())
            self.db.add(obj)
        if flush:
            self.db.flush()
        else:
            self.db.commit()
        self.db.refresh(obj)
        return obj

    def create(
        self,
        obj: tp.Generic[ModelType],
        flush: tp.Optional[bool] = None,
    ) -> tp.Generic[ModelType]:
        self.db.add(obj)

        if flush:
            self.db.flush()
        else:
            self.db.commit()

        self.db.refresh(obj)
        return obj

    def bulk_create(
        self,
        objs: tp.Generic[ModelType],
        flush: tp.Optional[bool] = None,
    ):
        self.db.add_all(objs)

        if flush:
            self.db.flush()
        else:
            self.db.commit()

        for obj in objs:
            self.db.refresh(obj)

        return objs

    def update(
        self,
        obj: tp.Generic[ModelType],
        obj_update: tp.Generic[PydanticModelType],
        flush: tp.Optional[bool] = None,
    ):
        for key, value in obj_update:
            if key not in obj_update.__fields_set__:
                continue
            if isinstance(value, BaseModel) or type(value) == list:
                pass
            else:
                setattr(obj, key, value)

        if flush:
            self.db.flush()
        else:
            self.db.commit()

        return obj

    def bulk_delete(
        self,
        objs: tp.Generic[ModelType],
        flush: tp.Optional[bool] = None,
    ):
        for obj in objs:
            self.db.delete(obj)
        if flush:
            self.db.flush()
        else:
            self.db.commit()
