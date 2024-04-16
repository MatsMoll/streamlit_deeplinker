from pydantic import BaseModel
from streamlit_deeplinker.router import deeplink_for

class StateA(BaseModel):
    name: str

def test_generate_deeplink():

    link = deeplink_for(StateA(name="test"))

    assert "test" in link
