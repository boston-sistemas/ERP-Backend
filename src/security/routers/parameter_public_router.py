from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.security.loaders import (
    FabricTypes,
    FiberCategories,
    FiberDenominations,
    ServiceOrderStatus,
    SpinningMethods,
    UserPasswordPolicy,
)
from src.security.schemas import (
    DataTypeListSchema,
    FabricTypesSchema,
    FiberCategoriesSchema,
    FiberDenominationsSchema,
    ServiceOrderStatusSchema,
    SpinningMethodsSchema,
    UserPasswordPolicySchema,
)

router = APIRouter()


@router.get("/data-types", response_model=DataTypeListSchema)
async def read_datatypes():
    return DataTypeListSchema


@router.get("/fiber-categories", response_model=FiberCategoriesSchema)
async def read_fiber_categories(db: AsyncSession = Depends(get_db)):
    return FiberCategoriesSchema(fiber_categories=await FiberCategories(db=db).get())


@router.get("/password-rules", response_model=UserPasswordPolicySchema)
async def password_restrictions(db: AsyncSession = Depends(get_db)):
    return await UserPasswordPolicy(db=db).get_schema()


@router.get("/spinning-methods", response_model=SpinningMethodsSchema)
async def read_spinning_methods(db: AsyncSession = Depends(get_db)):
    return SpinningMethodsSchema(spinning_methods=await SpinningMethods(db=db).get())


@router.get("/fabric-types", response_model=FabricTypesSchema)
async def read_fabric_types(db: AsyncSession = Depends(get_db)):
    return FabricTypesSchema(fabric_types=await FabricTypes(db=db).get())


@router.get("/service-order-status", response_model=ServiceOrderStatusSchema)
async def read_service_order_status(db: AsyncSession = Depends(get_db)):
    return ServiceOrderStatusSchema(
        service_order_status=await ServiceOrderStatus(db=db).get()
    )


@router.get("/fiber-denominations", response_model=FiberDenominationsSchema)
async def read_fiber_denominations(db: AsyncSession = Depends(get_db)):
    return FiberDenominationsSchema(
        fiber_denominations=await FiberDenominations(db=db).get()
    )
