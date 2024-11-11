import os
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Awaitable, Callable

import uvicorn
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI, Request

from drasi_reaction.logger import logger
from drasi_reaction.models.events import ChangeEvent, ControlEvent

AsyncChangeEventFunc = Callable[[ChangeEvent, dict[Any, Any] | None], Awaitable[Any]]

AsyncControlEventFunc = Callable[[ControlEvent, dict[Any, Any] | None], Awaitable[Any]]


class DrasiReaction:
    def __init__(
        self,
        on_change_event: AsyncChangeEventFunc,
        on_control_event: AsyncControlEventFunc | None = None,
        parse_query_configs: Callable[[TextIOWrapper], Any] | None = None,
    ) -> None:
        self.on_change_event = on_change_event
        self.on_control_event = on_control_event
        self.parse_query_configs = parse_query_configs

        self.pubsub_name = os.getenv("PubsubName", "drasi-pubsub")
        self.config_directory = Path(os.getenv("QueryConfigPath", "/etc/queries"))

        self._app = FastAPI()
        self._dapr_app = DaprApp(self._app)
        self._query_configs: dict[Any, Any] = {}
        self._subscribed = False

    def subscribe(self):
        if self.config_directory.is_dir():
            for query_path in self.config_directory.iterdir():
                if query_path.is_file() and not query_path.name.startswith("."):
                    query_id = query_path.stem

                    logger.info(f"subscribing to query {query_id}")
                    self.register_handler(query_id)

                    if self.parse_query_configs:
                        with open(query_path, "r") as f:
                            self._query_configs[query_id] = self.parse_query_configs(f)
        else:
            logger.warning(
                f"query directory {str(self.config_directory)} does not exist"
            )
        self._subscribed = True

    @property
    def query_configs(self):
        """The query_configs property."""

        return self._query_configs

    def start(self):
        try:
            if not self._subscribed:
                self.subscribe()

            logger.info("starting python reaction app")
            uvicorn.run(self._app, host="0.0.0.0", port=80)

        except Exception as err:
            logger.exception("error while running app:", err)
            exit(1)

    def stop(self):
        ...

    def register_handler(self, query_id):
        @self._dapr_app.subscribe(
            pubsub=self.pubsub_name, topic=f"{query_id}-results", route=f"/{query_id}"
        )
        async def handler(context: Request):
            context_body = await context.json()
            data = context_body.get("data", [])

            query_config = self.query_configs.get(data.get("queryId"))

            kind = data.get("kind")
            if kind == "change":
                change_data = ChangeEvent.model_validate(data)
                await self.on_change_event(change_data, query_config)

            if kind == "control" and self.on_control_event:
                control_data = ControlEvent.model_validate(data)
                await self.on_control_event(control_data, query_config)

        return handler
