import uuid
from typing import (
    Annotated,
    Callable,
)

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    status,
)
from pydantic import BaseModel
from sqlalchemy.orm import InstrumentedAttribute

from libs.cp_common.models.exceptions.http import (
    RequestedDataNotFoundHTTPException,
    UnprocessableEntityHTTPException,
)
from libs.cp_common.models.pydantic import (
    DeleteResult,
    HTTPExceptionResponse,
    MetaList,
    MultiDeleteResponse,
    NoneValidationMixin,
    ViewList,
    ViewListQueries,
)
from libs.cp_common.models.pydantic.api import DetailItem
from libs.cp_postgresql import BaseDatabaseGeneric
from libs.cp_postgresql.models.dto import (
    CreateTableFilterDTO,
    UserAuthorizedDTO,
)
from libs.cp_postgresql.models.pydantic import BaseFilter
from libs.cp_postgresql.models.sqlalchemy import OrmModel


class APIGenericRouter(APIRouter):
    """Register conventional CRUD and saved-filter routes for a repository.

    The router generates FastAPI endpoint functions around typed generic
    repositories while preserving caller-provided authentication and path
    dependencies.
    """

    def __init__(
        self,
        entity: str,
        generic_rep: BaseDatabaseGeneric,
        filters_generic_rep: BaseDatabaseGeneric | None = None,
        url_entity_id_name: str | None = None,
        **kwargs,
    ):
        """Initialize a generic entity router.

        Args:
            entity: Entity name used in route summaries and default path keys.
            generic_rep: Repository serving the entity routes.
            filters_generic_rep: Optional repository serving saved filters.
            url_entity_id_name: Optional entity-ID path parameter name.
            **kwargs: Additional ``APIRouter`` initialization arguments.
        """
        super().__init__(**kwargs)
        self.entity = entity
        self.generic_rep: BaseDatabaseGeneric = generic_rep
        self.url_entity_id_name = url_entity_id_name or entity + "_id"
        self.filters_generic_rep = filters_generic_rep

    def add_get_route(
        self,
        route: str,
        response_model: type[BaseModel],
        path_injection: Callable[..., uuid.UUID],
        auth_injection: Callable[..., UserAuthorizedDTO],
    ) -> None:
        """Register a route that retrieves one entity by ID."""

        @self.get(
            path=route,
            status_code=status.HTTP_200_OK,
            summary=f"Get the {self.entity}.",
            response_model=response_model,
            responses={
                status.HTTP_200_OK: {"model": response_model},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def get_entity(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            id_: Annotated[uuid.UUID, Depends(path_injection)],
            request: Request,
        ):
            """Resolve path context and retrieve one entity."""

            path_params = request.path_params
            path_params.pop(self.url_entity_id_name)
            return await self._get_entity(id_=id_, path_params=path_params, response_model=response_model)

    async def _get_entity(self, id_: uuid.UUID, path_params: dict, response_model: type[BaseModel]) -> BaseModel:
        """Retrieve and validate one entity response.

        Raises:
            RequestedDataNotFoundHTTPException: If the repository finds no entity.
        """
        entity = await self.generic_rep.get(id=id_, **path_params)
        if not entity:
            raise RequestedDataNotFoundHTTPException()
        return response_model.model_validate(entity)

    def add_get_list_route(
        self,
        route: str,
        response_model: type[ViewList],
        query_model: type[ViewListQueries],
        search_column: InstrumentedAttribute[str],
        list_item_model: type[BaseModel],
        auth_injection: Callable[..., UserAuthorizedDTO],
    ):
        """Register a paginated entity-list route."""

        @self.get(
            path=route,
            status_code=status.HTTP_200_OK,
            summary=f"Get the {self.entity} list.",
            response_model=response_model,
            responses={
                status.HTTP_200_OK: {"model": response_model},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def get_list_entity(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            queries: Annotated[ViewListQueries, Depends(query_model)],
            request: Request,
        ):
            """Resolve list queries and return an entity page."""

            return await self._get_list_entity(
                response_model=response_model,
                queries=queries,
                search_column=search_column,
                list_item_model=list_item_model,
                objects_to_get_by=request.path_params,
            )

    async def _get_list_entity(
        self,
        response_model: type[ViewList],
        queries: ViewListQueries,
        search_column: InstrumentedAttribute[str],
        list_item_model: type[BaseModel],
        objects_to_get_by: dict[str, uuid.UUID],
    ):
        """Retrieve a paginated entity list and its total count."""

        entities = await self.generic_rep.get_paginated_list(
            queries=queries,
            search_column=search_column,
            **objects_to_get_by,
        )

        total_count = await self.generic_rep.get_count(
            search=queries.search,
            search_column=search_column,
            **objects_to_get_by,
        )
        return response_model(
            data=[list_item_model.model_validate(entity) for entity in entities],
            meta=MetaList(
                total_count=total_count,
                offset=queries.offset,
                limit=queries.limit,
            ),
        )

    def add_delete_route(
        self,
        route: str,
        path_injection: Callable[..., uuid.UUID],
        auth_injection: Callable[..., UserAuthorizedDTO],
    ):
        """Register a route that deletes one entity by ID."""

        @self.delete(
            path=route,
            status_code=status.HTTP_204_NO_CONTENT,
            summary=f"Delete the {self.entity} by its ID.",
            response_model=None,
            responses={
                status.HTTP_204_NO_CONTENT: {"model": None},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def delete_entity(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            id_: Annotated[uuid.UUID, Depends(path_injection)],
            request: Request,
        ):
            """Resolve path context and delete one entity."""

            path_params = request.path_params
            path_params.pop(self.url_entity_id_name)
            return await self._delete_entity(id_=id_, path_params=request.path_params)

    async def _delete_entity(self, id_: uuid.UUID, path_params: dict):
        """Delete one entity or raise the shared not-found exception."""

        entity = await self.generic_rep.delete(id=id_, **path_params)
        if not entity:
            raise RequestedDataNotFoundHTTPException()
        return True

    def add_bulk_delete_route(
        self,
        route: str,
        response_model: type[MultiDeleteResponse],
        auth_injection: Callable[..., UserAuthorizedDTO],
        bulk_delete_limit=100,
    ):
        """Register a bounded bulk-delete route."""

        @self.delete(
            path=route,
            status_code=status.HTTP_200_OK,
            summary=f"Bulk delete the {self.entity}.",
            response_model=None,
            responses={
                status.HTTP_200_OK: {"model": response_model},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def bulk_delete_entity(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            ids: Annotated[
                list[uuid.UUID],
                Query(
                    max_length=bulk_delete_limit,
                    description="IDs to delete.",
                ),
            ],
            request: Request,
        ):
            """Delete requested IDs and return per-ID outcomes."""

            return await self._bulk_delete_entity(
                ids=ids,
                response_model=response_model,
                path_params=request.path_params,
            )

    async def _bulk_delete_entity(
        self,
        ids: list[uuid.UUID],
        response_model: type[MultiDeleteResponse],
        path_params: dict,
    ):
        """Delete multiple entities and build per-ID result records."""

        deleted_entities = await self.generic_rep.delete_many(ids=ids, **path_params)
        deleted_ids = {entity.id for entity in deleted_entities}
        records = [DeleteResult(deleted=id_ in deleted_ids, id=id_) for id_ in ids]
        return response_model(records=records)

    def add_post_route(
        self,
        route: str,
        response_model: type[BaseModel],
        request_model: type[BaseModel],
        auth_injection: Callable[..., UserAuthorizedDTO],
    ):
        """Register a route that creates one entity."""

        @self.post(
            path=route,
            status_code=status.HTTP_201_CREATED,
            summary=f"Create the {self.entity}.",
            response_model=response_model,
            responses={
                status.HTTP_201_CREATED: {"model": response_model},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def create_entity(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            entity_api_model: request_model,
            request: Request,
        ):
            """Build a creation DTO from request and path fields."""

            dto_model = self.generic_rep.model_create(**entity_api_model.model_dump(), **request.path_params)
            return await self._create_entity(
                response_model=response_model,
                dto=dto_model,
            )

    async def _create_entity(
        self,
        dto: OrmModel,
        response_model: type[BaseModel],
    ):
        """Persist a creation DTO and validate its response model."""

        entity = await self.generic_rep.create(model=dto)
        return response_model.model_validate(entity)

    def add_patch_route(
        self,
        route: str,
        response_model: type[BaseModel],
        request_model: type[NoneValidationMixin],
        path_injection: Callable[..., uuid.UUID],
        auth_injection: Callable[..., UserAuthorizedDTO],
        update_user_id: bool = False,
    ):
        """Register a route that partially updates one entity."""

        @self.patch(
            path=route,
            status_code=status.HTTP_200_OK,
            summary=f"Update the {self.entity}.",
            response_model=response_model,
            responses={
                status.HTTP_200_OK: {"model": response_model},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def update_entity(
            user: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            id_: Annotated[uuid.UUID, Depends(path_injection)],
            entity_model_api: request_model,
            request: Request,
        ):
            """Resolve update context and apply partial entity fields."""

            path_params = request.path_params
            path_params.pop(self.url_entity_id_name)
            return await self._update_entity(
                user=user,
                id_=id_,
                response_model=response_model,
                entity_model_api=entity_model_api,
                update_user_id=update_user_id,
                path_params=request.path_params,
            )

    async def _update_entity(
        self,
        user: UserAuthorizedDTO,
        id_: uuid.UUID,
        response_model: type[BaseModel],
        entity_model_api: NoneValidationMixin,
        path_params: dict,
        update_user_id: bool = False,
    ):
        """Update an entity and validate its response model.

        Raises:
            RequestedDataNotFoundHTTPException: If no matching entity is updated.
        """
        entity_update_dto = self.generic_rep.model_update(**entity_model_api.model_dump(exclude_unset=True))
        if update_user_id:
            entity_updated = await self.generic_rep.update(
                id=id_,
                updated_by_id=user.id,
                data=entity_update_dto,
                **path_params,
            )
        else:
            entity_updated = await self.generic_rep.update(id=id_, data=entity_update_dto, **path_params)
        if not entity_updated:
            raise RequestedDataNotFoundHTTPException()
        return response_model.model_validate(entity_updated)

    def add_get_list_of_filters_route(
        self,
        route: str,
        response_model: type[BaseModel],
        list_item_model: type[BaseModel],
        auth_injection: Callable[..., UserAuthorizedDTO],
        filters_table: str,
        filters_field: str = "filter",
    ):
        """Register a route that lists the current user's saved filters."""

        @self.get(
            path=route,
            status_code=status.HTTP_200_OK,
            summary=f"Get the {self.entity} filters list.",
            response_model=response_model,
            responses={
                status.HTTP_200_OK: {"model": response_model},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def add_get_list_of_filters(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            request: Request,
        ):
            """Resolve user scope and return saved filters."""

            select_filters = {
                "user_id": auth.id,
                "project_id": auth.project_id,
                "table": filters_table,
            }
            return await self._get_list_of_filters(
                response_model=response_model,
                list_item_model=list_item_model,
                objects_to_get_by=select_filters,
                filters_field=filters_field,
            )

    async def _get_list_of_filters(
        self,
        response_model: type[BaseModel],
        list_item_model: type[BaseModel],
        objects_to_get_by: dict,
        filters_field: str = "filter",
    ):
        """Load saved filters and flatten their filter payloads for the API."""

        filters = await self.filters_generic_rep.get_list(**objects_to_get_by)

        return response_model(
            data=[
                list_item_model(**filter_.model_dump(exclude={"data"}), **getattr(filter_, filters_field).model_dump())
                for filter_ in filters
            ],
        )

    def add_delete_filter_route(
        self,
        route: str,
        path_injection: Callable[..., uuid.UUID],
        auth_injection: Callable[..., UserAuthorizedDTO],
    ):
        """Register a route that deletes one saved filter."""

        @self.delete(
            path=route,
            status_code=status.HTTP_200_OK,
            summary=f"Delete the {self.entity}`s filter.",
            response_model=None,
            responses={
                status.HTTP_200_OK: {"model": None},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def add_delete_filter(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            id_: Annotated[uuid.UUID, Depends(path_injection)],
            request: Request,
        ):
            """Delete a saved filter by its resolved identifier."""

            return await self._delete_filter(id_=id_)

    async def _delete_filter(
        self,
        id_: uuid.UUID,
    ) -> bool:
        """Delete one saved filter or raise the shared not-found exception."""

        filter_ = await self.filters_generic_rep.delete(id=id_)
        if not filter_:
            raise RequestedDataNotFoundHTTPException()
        return True

    def add_post_filter_route(
        self,
        route: str,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
        auth_injection: Callable[..., UserAuthorizedDTO],
        validation_function: Callable,
        filters_table: str,
    ):
        """Register a route that creates a validated saved filter."""

        @self.post(
            path=route,
            status_code=status.HTTP_201_CREATED,
            summary=f"Create the {self.entity}`s filter.",
            response_model=response_model,
            responses={
                status.HTTP_201_CREATED: {"model": response_model},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def create_filter(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            filter_api_model: request_model,
            request: Request,
        ):
            """Validate and persist a saved filter for the current user."""

            return await self._create_filter(
                auth=auth,
                response_model=response_model,
                validation_function=validation_function,
                filter_api_model=filter_api_model,
                filters_table=filters_table,
            )

    async def _create_filter(
        self,
        auth: UserAuthorizedDTO,
        filter_api_model: BaseModel,
        response_model: type[BaseModel],
        validation_function: Callable,
        filters_table: str,
    ):
        """Validate, scope, and persist a saved filter.

        Raises:
            UnprocessableEntityHTTPException: If the supplied filter is invalid.
        """
        try:
            filter_ = validation_function(filter_api_model.filter.model_dump())
        except ValueError:
            raise UnprocessableEntityHTTPException(
                detail=DetailItem(
                    message="Некорректный фильтр",
                    code=UnprocessableEntityHTTPException.code,
                ),
            )
        dto = CreateTableFilterDTO(
            id=filter_api_model.id,
            project_id=auth.project_id,
            user_id=auth.id,
            table=filters_table,
            filter=BaseFilter(**filter_.model_dump(mode="json")),
        )
        created_filter = await self.filters_generic_rep.create(model=dto)
        return response_model(
            id=created_filter.id,
            op=created_filter.filter.op,
            field=created_filter.filter.field,
            value=created_filter.filter.value,
        )

    def add_patch_filter_route(
        self,
        route: str,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
        auth_injection: Callable[..., UserAuthorizedDTO],
        path_injection: Callable[..., uuid.UUID],
        validation_function: Callable,
        filters_table: str,
    ):
        """Register a route that partially updates one saved filter."""

        @self.patch(
            path=route,
            status_code=status.HTTP_201_CREATED,
            summary=f"Update the {self.entity}`s filter.",
            response_model=response_model,
            responses={
                status.HTTP_201_CREATED: {"model": response_model},
                status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
                status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
                status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPExceptionResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionResponse},
            },
        )
        async def create_filter(
            auth: Annotated[UserAuthorizedDTO, Depends(auth_injection)],
            filter_api_model: request_model,
            id_: Annotated[uuid.UUID, Depends(path_injection)],
            request: Request,
        ):
            """Validate and update a saved filter owned by the current user."""

            return await self._update_filter(
                id_=id_,
                auth=auth,
                response_model=response_model,
                filter_api_model=filter_api_model,
                filters_table=filters_table,
                validation_function=validation_function,
            )

    async def _update_filter(
        self,
        id_: uuid.UUID,
        auth: UserAuthorizedDTO,
        filter_api_model: BaseModel,
        filters_table: str,
        response_model: type[BaseModel],
        validation_function: Callable,
    ):
        """Load, validate, and update a user-owned saved filter.

        Raises:
            RequestedDataNotFoundHTTPException: If the scoped filter is absent.
            UnprocessableEntityHTTPException: If the merged filter is invalid.
        """
        async with self.filters_generic_rep.database.session() as session:
            filter_ = await self.filters_generic_rep.get(
                id=id_,
                project_id=auth.project_id,
                user_id=auth.id,
                table=filters_table,
                session=session,
            )
            if not filter_:
                raise RequestedDataNotFoundHTTPException()
            try:
                dict_filter = filter_.filter.model_dump()
                dict_filter.update(filter_api_model.model_dump())
                filter_ = validation_function(dict_filter)
            except ValueError:
                raise UnprocessableEntityHTTPException(
                    detail=DetailItem(
                        message="Некорректный фильтр",
                        code=UnprocessableEntityHTTPException.code,
                    ),
                )

            updated = await self.filters_generic_rep.update(
                id=id_,
                data=self.filters_generic_rep.model_update(filter=BaseFilter(**filter_.model_dump(mode="json"))),
                table=filters_table,
                session=session,
            )
        return response_model(
            id=updated.id,
            field=updated.filter.field,
            op=updated.filter.op,
            value=updated.filter.value,
        )
