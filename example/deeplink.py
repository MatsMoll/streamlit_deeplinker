from streamlit_deeplinker import deeplinks, set_deeplink
import streamlit as st
from pydantic import BaseModel

class StateA(BaseModel):
    name: str

class StateB(BaseModel):
    name: str
    click: int


def page_a(state: StateA):
    st.title("Page A")
    st.write(f"Hello {state.name}")

    if st.button("Click me"):
        state.name = "World"
        set_deeplink(state)
    
    if st.button("Go back"):
        set_deeplink(None)

def page_b(state: StateB):
    st.title("Page B")
    st.write(f"Hello {state.name * state.click}")
    st.write(f"Clicks: {state.click}")

    if st.button("Click me"):
        state.click += 1
        set_deeplink(state)

    if st.button("Reset"):
        set_deeplink(None)


@deeplinks(
    deeplinks={ # type: ignore
        StateA: page_a,
        StateB: page_b
    }
)
def app():
    st.title("Deeplink Example")

    st.write("This is the landing page. You can navigate to other pages using the sidebar.")







