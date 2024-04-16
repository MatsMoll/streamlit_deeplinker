from pydantic import BaseModel
from typing import Callable, Awaitable, Literal, NoReturn, TypeVar
from dataclasses import dataclass
import streamlit as st
from streamlit.components.v1 import html
from streamlit.delta_generator import DeltaGenerator
from time import sleep
from inspect import iscoroutinefunction


T = TypeVar("T", bound=BaseModel)


def has_deeplink() -> bool:
    return st.query_params.get("sn") is not None


def set_deeplink(state: BaseModel | None) -> NoReturn | None:
    """
    Sets a deeplink for the given state. If the state is None, it will clear the current deeplink.

    ```python
    class StateA(BaseModel):
        name: str

    state = StateA(name="Hello")
    set_deeplink(state)

    # Set initial state
    set_deeplink(None)
    """
    wait_duration = 0.05


    if state is None:
        if not has_deeplink():
            return

        st.query_params.clear()
        sleep(wait_duration)
        st.rerun()

    current = read_deeplink(state.__class__)
    if current == state:
        return

    encoded = state.model_dump_json()
    link = deeplink_for(state)
    push_state_script = f"<script>window.history.pushState({{state: {state.__class__.__name__}}}, '', '{link}')</script>"
    html(push_state_script, height=0)

    st.query_params["sn"] = state.__class__.__name__
    st.query_params["state"] = encoded

    sleep(wait_duration)
    st.rerun()


def read_deeplink(state: type[T]) -> T | None | Exception:
    try:
        if st.query_params.get("sn") == state.__name__:
            return state.parse_raw(st.query_params["state"])
        return None
    except Exception as e:
        return e


def deeplink_for(state: BaseModel) -> str:
    return f"sn={state.__class__.__name__}&state={state.model_dump_json()}"


@dataclass
class StreamlitConfig:
    title: str
    icon: str
    layout: Literal["wide", "centered"]


DeeplinkInitialRoute = Callable[[], Awaitable[None]] | Callable[[], None]

@dataclass
class DeeplinkRouter:

    initial_route: DeeplinkInitialRoute
    routes: dict[type[BaseModel], Callable[[BaseModel], Awaitable[None]] | Callable[[BaseModel], None]]
    sidebar: Callable[[DeltaGenerator], Awaitable[None]] | Callable[[DeltaGenerator], None] | None = None
    config: StreamlitConfig | None = None
    url_path: str = "/"

    def run(self) -> None:

        if iscoroutinefunction(self.initial_route):
            raise ValueError("The initial route function should be a coroutine. Consider running `arun` in stead.")

        if self.config is not None:
            st.set_page_config(
                page_title=self.config.title,
                page_icon=self.config.icon,
                layout=self.config.layout
            )

        if self.sidebar is not None:
            if iscoroutinefunction(self.sidebar):
                raise ValueError("The sidebar function should not be a coroutine. Consider running `arun` in stead.")

            self.sidebar(st.sidebar)

        if not has_deeplink():

            self.initial_route()
            return


        for state_type, route in self.routes.items():
            state = read_deeplink(state_type)

            if isinstance(state, Exception):
                st.error(f"Unable to parse the given deeplink. Therefore, showing the landing route.")
                st.error(state)
                self.initial_route()
                return

            if state is not None:
                if iscoroutinefunction(route):
                    raise ValueError("The route functions should not be coroutines. Consider running `arun` in stead.")
                route(state)
                return

        st.warning("Unable to parse the given deeplink. Therefore, showing the landing route.")
        self.initial_route()

    async def arun(self) -> None:

        async def run_callable(callable: Callable) -> None:
            if iscoroutinefunction(callable):
                await callable()
            else:
                callable()

        if self.config is not None:
            st.set_page_config(
                page_title=self.config.title,
                page_icon=self.config.icon,
                layout=self.config.layout
            )

        if self.sidebar is not None:
            if iscoroutinefunction(self.sidebar):
                await self.sidebar(st.sidebar)
            else:
                self.sidebar(st.sidebar)

        if not has_deeplink():
            await run_callable(self.initial_route)
            return

        for state_type, route in self.routes.items():
            state = read_deeplink(state_type)

            if isinstance(state, Exception):
                st.error(f"Unable to parse the given deeplink. Therefore, showing the landing route.")
                st.error(state)
                await run_callable(self.initial_route)
                return

            if state is not None:
                if iscoroutinefunction(route):
                    await route(state)
                else:
                    route(state)
                return

        st.warning("Unable to parse the given deeplink. Therefore, showing the landing route.")
        await run_callable(self.initial_route)


    def start(self) -> None:
        use_async = any([
            iscoroutinefunction(self.initial_route), 
            iscoroutinefunction(self.sidebar), 
            any([iscoroutinefunction(route) for route in self.routes.values()])
        ])

        if use_async:
            import asyncio
            asyncio.run(self.arun())
        else:
            self.run()



def deeplinks(
    deeplinks: dict[
        type[BaseModel], 
        Callable[[BaseModel], Awaitable[None]] | Callable[[BaseModel], None]
    ],
    sidebar: Callable[[DeltaGenerator], Awaitable[None]] | Callable[[DeltaGenerator], None] | None = None,
    config: StreamlitConfig | None = None,
    path: str = "/"
) -> Callable[[DeeplinkInitialRoute], DeeplinkRouter]:
    """
    Creates a deeplink router for.

    ```python
    @deeplinks({
        StateA: page_a,
        StateB: page_b
    })
    def app():
        st.write("This is the landing page. You can navigate to other pages using the sidebar.")

    if __main__ == "__main__":
        app.main()
    ```
    """

    def decorator(initial_route: DeeplinkInitialRoute) -> DeeplinkRouter:
        return DeeplinkRouter(initial_route, deeplinks, sidebar, config, path)

    return decorator
