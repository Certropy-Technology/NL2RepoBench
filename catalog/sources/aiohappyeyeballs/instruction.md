# Project Description

Create a complete, installable Python distribution named `aiohappyeyeballs`.
It is a pure-Python asyncio helper for opening a TCP socket after the caller
has already resolved a hostname into `getaddrinfo`-style records. The package
implements a local Happy Eyeballs connection race and utilities for preparing
and mutating address-info lists.

# Supports

- Support Python 3.10 and newer, including Python 3.12.
- Install from the repository root using `python -m pip install .` with no
  network access after the declared build requirement is available.
- Use distribution name `aiohappyeyeballs`, version `2.7.1`, and import package
  `aiohappyeyeballs` with a `py.typed` marker.
- Declare no third-party runtime dependencies. The only build-system
  requirement is `poetry-core>=2.0.0`.
- Normal operation is local asyncio and socket work. It must not resolve DNS,
  access the public network, start a long-lived service, or require files
  outside the installed package.

# API Usage Guide

## Root exports

`aiohappyeyeballs.__all__` contains these names in this order:

```text
AddrInfoType, SocketFactoryType, addr_to_addr_infos,
pop_addr_infos_interleave, remove_addr_infos, start_connection
```

`AddrInfoType` describes an address-info record as
`(family, type, proto, canonname, sockaddr)`. `SocketFactoryType` is a callable
accepting one such record and returning a `socket.socket`.

## `addr_to_addr_infos`

```python
addr_to_addr_infos(
    addr: tuple[str, int] | tuple[str, int, int] | tuple[str, int, int, int] | None,
) -> list[AddrInfoType] | None
```

Return `None` when `addr` is `None`. For an IPv4 host, return one TCP/IP
`AF_INET` record whose socket address is `(host, port)`. For a host containing
`:` return one TCP/IP `AF_INET6` record with `(host, port, flowinfo, scopeid)`;
missing IPv6 flow and scope fields default to zero. The returned list is a new
object.

## Address-list mutation helpers

```python
pop_addr_infos_interleave(addr_infos: list[AddrInfoType], interleave: int | None = None) -> None
remove_addr_infos(
    addr_infos: list[AddrInfoType],
    addr: tuple[str, int] | tuple[str, int, int, int],
) -> None
```

Both functions mutate `addr_infos` in place and return `None`.

`pop_addr_infos_interleave` removes the first `interleave` records for every
address family while preserving the relative order of records that remain.
`None` means one record per family. `remove_addr_infos` removes every record
whose socket address matches `addr`. Address spelling differences that denote
the same IPv4 or IPv6 address are treated as equal. Raise `ValueError` when no
record is removed.

## `start_connection`

```python
async def start_connection(
    addr_infos: Sequence[AddrInfoType],
    *,
    local_addr_infos: Sequence[AddrInfoType] | None = None,
    happy_eyeballs_delay: float | None = None,
    interleave: int | None = None,
    loop: asyncio.AbstractEventLoop | None = None,
    socket_factory: SocketFactoryType | None = None,
) -> socket.socket
```

Open and return a non-blocking TCP socket connected to the first successful
destination. `addr_infos` must be non-empty or the function raises
`ValueError`. Without a delay, destinations are attempted sequentially. With a
delay, later attempts begin when the previous attempt fails or its delay
expires; if `interleave` is omitted in this mode, interleave families one at a
time first. If `local_addr_infos` is supplied, bind a same-family local address
before connecting. If `socket_factory` is supplied, call it with the selected
address-info record instead of creating the socket directly.

When every attempt fails, raise a representative connection exception. On a
successful race, close any non-winning sockets and return the winning socket.
The caller owns and must close the returned socket.

# Implementation Notes

Use standard-library `asyncio`, `socket`, `contextlib`, and collection helpers.
Preserve the caller's address-info list except where a documented mutation
helper is explicitly used. Treat cancellation, `KeyboardInterrupt`, and
`SystemExit` as control flow rather than ordinary connection errors. Do not
retrieve an upstream repository or reference implementation at runtime.
