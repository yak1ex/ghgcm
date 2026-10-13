"""Read-only bindings for the Windows Credential API."""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

from .models import RawCredential

CRED_TYPE_GENERIC = 1
CRED_ENUMERATE_ALL_CREDENTIALS = 0x1
ERROR_NOT_FOUND = 1168


class CredentialEnumerationError(RuntimeError):
    """Raised when Windows refuses or fails to enumerate credentials."""

    def __init__(self, error_code: int):
        self.error_code = error_code
        super().__init__(f"Windows credential enumeration failed (error {error_code})")


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


class CREDENTIALW(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


PCREDENTIALW = ctypes.POINTER(CREDENTIALW)


def enumerate_credentials() -> list[RawCredential]:
    """Copy credentials from the current user's vault without modifying it."""

    if sys.platform != "win32":
        raise OSError("wincredman inventory is supported only on Windows")

    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    cred_enumerate = advapi32.CredEnumerateW
    cred_enumerate.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(ctypes.POINTER(PCREDENTIALW)),
    ]
    cred_enumerate.restype = wintypes.BOOL
    cred_free = advapi32.CredFree
    cred_free.argtypes = [ctypes.c_void_p]
    cred_free.restype = None

    count = wintypes.DWORD()
    credentials = ctypes.POINTER(PCREDENTIALW)()
    if not cred_enumerate(None, CRED_ENUMERATE_ALL_CREDENTIALS, ctypes.byref(count), ctypes.byref(credentials)):
        error_code = ctypes.get_last_error()
        if error_code == ERROR_NOT_FOUND:
            return []
        raise CredentialEnumerationError(error_code)

    result: list[RawCredential] = []
    try:
        for index in range(count.value):
            item = credentials[index].contents
            blob = (
                bytes(ctypes.string_at(item.CredentialBlob, item.CredentialBlobSize))
                if item.CredentialBlobSize and bool(item.CredentialBlob)
                else b""
            )
            result.append(RawCredential(item.TargetName or "", item.UserName, blob, item.Type))
    finally:
        cred_free(credentials)
    return result
