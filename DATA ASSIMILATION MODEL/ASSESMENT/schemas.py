# schemas.py  ────────────────────────────────────────────────────────────────
from typing import List, Dict
from pydantic import BaseModel

class WelchBlock(BaseModel):
    frequencies: List[float]
    power: Dict[str, List[float]]   # keys: All, Original, WC, NWC

class RunResponse(BaseModel):
    # Kalman time-domain outputs
    y_all:           List[float]
    y_winningcomb:   List[float]
    y_nonwinning:    List[float]

    amplitude_all:        List[float]
    amplitude_winning:    List[float]
    amplitude_nonwinning: List[float]
    amplitude_original:   List[float]

    # Welch bundle
    welch: WelchBlock
