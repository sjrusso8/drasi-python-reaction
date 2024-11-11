# Drasi Python SDK

This is a *way to early* python SDK for the [drasi-project](https://github.com/drasi-project/drasi-platform/tree/main). 

This is purely experimental and should not be used as an offical SDK.

## Usage

When a continuous query is changed, a message is published to a Dapr topic. This simple SDK allows you to subscribe to the 
topics and register a handle for two types of data changes; `ChangeEvent` and, optionally,  `ControlEvent`.

Here is an example of creating a simple `on_change_event` function and registering the handler.

```python
import logging
from typing import Any

from drasi_reaction.models.events import ChangeEvent, ControlEvent
from drasi_reaction.sdk import DrasiReaction

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


async def change_event(data: ChangeEvent, query_configs: dict[Any, Any] | None = None):
    logger.info(f"handling change event")
    logger.info(data)


if __name__ == "__main__":
    reaction = DrasiReaction(on_change_event=change_event)

    reaction.start()
```

The configs for a reaction are defined in the yaml file to be deployed with drasi. Queri

## Example

To run the examples, it's best to have drasi running on a kind cluster with `--local`. To ensure drasi starts correctly, 
have the [drasi-platform](https://github.com/drasi-project/drasi-platform/tree/main) cloned and build the images directly from the repo. 

After the repo is clone and run the commands `make docker-build` and `make kind-load` in the root folder

Then start the drasi platform by running `drasi init --local --version latest`.

### Run the Python Example

The python example runs off of the same resources as used in the [Getting Started](https://drasi.io/getting-started/) example. 

Make sure those same resources are running on a drasi instance with `drasi init --local --version latest`

Once the local drasi instance is running, and all resources are healthy. Run the following commands

```bash
make docker-build && make kind-load
```

```bash
drasi apply -f ./examples/simple/python-reaction.yml
```
