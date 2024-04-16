# Streamlit Deeplinker

Set state deep in an application with ease. 

Make them navigatable through your broswer history, and shareable with other people through an URL.

## Install
Install with your favorite package manager

**Poetry**: `poetry add streamlit-deeplinker`

**Pip**: `pip install streamlit-deeplinker`

And then you can start creating deeplink applications like the following:

```python
from streamlit_deeplinker import deeplinks, set_deeplink
from pydantic import BaseModel

class StateA(BaseModel):
    name: str

async def page_a(state: StateA):
    st.write(f"Hello {state.name}")

    if st.button("Go back"):
        set_deeplink(None)

@deeplinks(
    deeplinks={
        StateA: page_a,
    }
)
def app():
    st.title("Deeplink Example")

    st.write("This is the landing page. You can navigate to other pages using the button bellow.")

    st.button("Next"):
        set_deeplink(StateA("World"))

app.start()
```

## Motivation
Streamlit is an awesome technology to get Python applications up and running with an UI.
However thier "run from top to bottom" structure can lead lead to issues when setting state deep down in the applications. Potentially making some state getting lost, or leading to a slow application.

Therefore, this package makes it possible to create dedicated pages for a given state. Leading to faster applications and less complex applications.


## Usage

The `streamlit_deeplinker`er works by routing the user state to differnet functions.

The state is assumed to be defined as `pydantic` models, as they will be encoded and decoded as url params.

> [!WARNING]  
> Encoding data in the URL params can lead to issues for large payload, as web browsers have different max URL lengths. Therefore, try to keep the state as light weight as possible.

Each `pydantic` model expects an associated function which can either be an `async` function or not. Then the `.start()` method will figure out if it needs to run the application through `asyncio`.

```python
@deeplinks(
    deeplinks={ # type: ignore
        StateA: page_a,
        StateB: page_b,
        ...
    }
)
def initial_page():
    ...
```


### Sidebar

You can also configure the sidebar in the `deeplinks` call, and then the router will make sure it is rendered for all the different deeplinks.


```python
from streamlit.delta_generator import DeltaGenerator

def render_sidebar(sidebar: DeltaGenerator):
    sidebar.title("Hello")

@deeplinks(
    deeplinks={ # type: ignore
        StateA: page_a,
        StateB: page_b,
        ...
    },
    sidebar=render_sidebar
)
def initial_page():
    ...
```


### Streamlit Config

Since the deeplink router do not run the initial page on deeplinks will it not be the best place to set streamlit configs. Therefore, is it possible to pass a `config` param to the `deeplinks` method.

```python
from streamlit_deeplinker import StreamlitConfig, deeplinks

@deeplinks(
    deeplinks={ # type: ignore
        StateA: page_a,
        StateB: page_b,
        ...
    },
    config=StreamlitConfig(
        title="My awesome application",
        icon=":book:",
        layout="wide"
    )
)
def initial_page():
    ...
```
