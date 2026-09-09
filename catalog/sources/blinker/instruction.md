# Build blinker Package from Scratch

## Project Description

`blinker` is a fast Python in-process signal/event dispatching system that allows application components to communicate through a loosely-coupled notification pattern. It provides a simple and efficient way to implement the observer pattern, supporting named signals, sender-specific connections, weak references, and flexible receiver management.

The package enables decoupled communication where senders can emit signals that trigger registered receivers (callbacks), with support for filtering receivers by sender identity and passing arbitrary keyword arguments.

## Supports

### Environment Configuration

- **Python Version**: 3.12
- **Operating System**: Debian 12 (amd64)
- **Runtime Dependencies**: None (pure Python, no external dependencies)
- **Build System**: flit-core (preinstalled in agent image)

### Project Directory Structure

```
workspace/
├── src/
│   └── blinker/
│       ├── __init__.py
│       ├── base.py
│       └── _utilities.py
├── pyproject.toml
├── LICENSE.txt
└── README.md
```

## API Usage Guide

### Core Signal Class

#### Creating Signals

```python
from blinker import Signal

# Create an anonymous signal
sig = Signal(doc="Optional documentation")
```

#### Named Signals

```python
from blinker import signal, Namespace

# Get or create a named signal from the default namespace
my_signal = signal('signal-name')

# Create a custom namespace
ns = Namespace()
custom_signal = ns.signal('custom-signal')
```

### Connecting Receivers

#### Basic Connection

```python
def my_receiver(sender, **kwargs):
    print(f"Received from {sender}")
    return "result"

# Connect with weak reference (default)
sig.connect(my_receiver)

# Connect with strong reference
sig.connect(my_receiver, weak=False)
```

#### Sender-Specific Connection

```python
# Only call receiver when specific sender emits
sig.connect(my_receiver, sender='specific-sender', weak=False)

# Connect to any sender (default)
from blinker import ANY
sig.connect(my_receiver, sender=ANY, weak=False)
```

#### Decorator Connection

```python
@sig.connect_via('sender-id', weak=False)
def decorated_receiver(sender, **kwargs):
    return "handled"
```

### Sending Signals

```python
# Send signal with sender as positional argument
results = sig.send('sender-id')
# Returns: [(receiver_func, return_value), ...]

# Send with additional keyword arguments
results = sig.send('sender-id', key='value', num=42)
# Receivers receive: receiver(sender='sender-id', key='value', num=42)
```

The `send()` method returns a list of tuples, where each tuple contains:
1. The receiver callable
2. The return value from that receiver

### Receiver Management

#### Checking for Receivers

```python
# Check if any receivers would be called for a sender
has_receivers = sig.has_receivers_for('sender-id')

# Iterate through receivers that would be called
for receiver in sig.receivers_for('sender-id'):
    print(receiver)

# Quick check using the receivers attribute
if sig.receivers:
    print("Signal has connected receivers")
```

#### Disconnecting Receivers

```python
# Disconnect from all senders
sig.disconnect(my_receiver)

# Disconnect from specific sender only
sig.disconnect(my_receiver, sender='specific-sender')
```

### Context Managers

#### Temporary Connection

```python
def temp_receiver(sender):
    return "temp"

# Receiver is automatically disconnected after the with block
with sig.connected_to(temp_receiver, sender='target'):
    sig.send('target')  # Receiver is called
sig.send('target')  # Receiver is not called
```

#### Muting Signals

```python
# Temporarily disable signal dispatching
sig.connect(lambda s: "test", weak=False)
sig.send('sender')  # Receivers called

with sig.muted():
    sig.send('sender')  # No receivers called

sig.send('sender')  # Receivers called again
```

### Namespaces

Namespaces organize named signals into separate collections:

```python
from blinker import Namespace, default_namespace

# Default namespace (used by signal() function)
sig1 = signal('my-signal')
sig2 = signal('my-signal')
assert sig1 is sig2  # Same signal

# Custom namespaces provide isolation
ns1 = Namespace()
ns2 = Namespace()
sig_a = ns1.signal('test')
sig_b = ns2.signal('test')
assert sig_a is not sig_b  # Different signals

# Access signals like a dictionary
sig = ns1['test']  # Same as ns1.signal('test')
```

### ANY Sender Symbol

The `ANY` symbol represents "any sender":

```python
from blinker import ANY

# Connect to receive from any sender
sig.connect(receiver, sender=ANY, weak=False)

# When sending, ANY-connected receivers are always called
# along with sender-specific receivers
```

### Meta Signals

Signals can emit meta-signals when receivers connect or disconnect:

```python
sig = Signal()

def on_connect(signal_sender, **kwargs):
    receiver = kwargs['receiver']
    sender = kwargs['sender']
    weak = kwargs['weak']
    print(f"Receiver {receiver} connected")

sig.receiver_connected.connect(on_connect, weak=False)

def on_disconnect(signal_sender, **kwargs):
    receiver = kwargs['receiver']
    sender = kwargs['sender']
    print(f"Receiver {receiver} disconnected")

sig.receiver_disconnected.connect(on_disconnect, weak=False)
```

## Implementation Notes

### Key Behavioral Details

1. **Return Values**: The `send()` method always returns a list of `(receiver, result)` tuples, even when no receivers are connected (empty list).

2. **Receiver Invocation**: When a signal is sent, all matching receivers are called immediately and synchronously. If a receiver raises an exception, it propagates to the caller.

3. **Sender Filtering**: 
   - Receivers connected with `sender=ANY` are called for any sender
   - Receivers connected with a specific sender are called only for that sender
   - When sending to a specific sender, both ANY-connected and sender-specific receivers are called

4. **Receiver Identity**: The same receiver function can be connected multiple times with different senders. However, connecting the same receiver with both ANY and a specific sender results in only one call (deduplicated by receiver identity).

5. **Weak References**: By default, receivers are stored using weak references, allowing automatic cleanup when the receiver is garbage collected. Use `weak=False` for receivers defined within function scopes to prevent premature cleanup.

6. **Named Signal Singleton**: Calling `signal('name')` or `namespace.signal('name')` multiple times with the same name returns the same signal instance.

7. **Muting Behavior**: When a signal is muted, calling `send()` returns an empty list. Nested muting contexts do not stack - the `is_muted` flag is simply set to True/False.

8. **Meta Signals**: The `receiver_connected` and `receiver_disconnected` signals are created on-demand (cached properties) and emit events when receivers are explicitly connected or disconnected.

### Installation

The package should be installable as an editable package from the workspace directory:

```bash
pip install --no-build-isolation --no-deps --no-index -e .
```

The build system requires `flit-core` which should be preinstalled in the agent image.

### Testing Your Implementation

After building the package, verify the core functionality:

```python
import blinker

# Test basic signal
sig = blinker.Signal()
results = []

def handler(sender, **kwargs):
    results.append((sender, kwargs))
    return 'success'

sig.connect(handler, weak=False)
send_results = sig.send('test-sender', key='value')

assert len(send_results) == 1
assert send_results[0][1] == 'success'
assert results[0] == ('test-sender', {'key': 'value'})

# Test named signals
sig1 = blinker.signal('test')
sig2 = blinker.signal('test')
assert sig1 is sig2

print("Basic tests passed!")
```
