"""Keep Windows from sleeping while a long job runs.

Uses SetThreadExecutionState (what media players use): no settings change, and the request
ends with the process. Closing the lid or a flat battery still suspends the machine.
"""
import sys


def keep_awake():
    if sys.platform == "win32":
        import ctypes
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
