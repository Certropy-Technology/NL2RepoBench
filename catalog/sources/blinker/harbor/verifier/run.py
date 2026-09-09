#!/usr/bin/env python3
"""Custom JSON v1 verifier for blinker package."""

import json
import sys
from nl2repobench.verification.candidate_client import execute_script

CASES: list[tuple[str, str, object]] = [
    # Basic Signal creation and sending
    ("basic_signal_creation", """
import blinker
sig = blinker.Signal()
result = {"type": type(sig).__name__}
""", {"ok": True, "value": {"type": "Signal"}}),

    ("signal_send_empty", """
import blinker
sig = blinker.Signal()
result = sig.send('sender1')
""", {"ok": True, "value": []}),

    ("signal_connect_and_send", """
import blinker
sig = blinker.Signal()
def handler(sender, **kwargs):
    return 'handler_result'
sig.connect(handler, weak=False)
send_results = sig.send('sender1')
result = {"len": len(send_results), "has_handler": handler in [r[0] for r in send_results], "return_val": send_results[0][1]}
""", {"ok": True, "value": {"len": 1, "has_handler": True, "return_val": "handler_result"}}),

    ("signal_send_with_kwargs", """
import blinker
sig = blinker.Signal()
received = []
def handler(sender, **kwargs):
    received.append((sender, kwargs))
    return 'ok'
sig.connect(handler, weak=False)
sig.send('sender1', key='value', num=42)
result = {"sender": received[0][0], "kwargs": received[0][1]}
""", {"ok": True, "value": {"sender": "sender1", "kwargs": {"key": "value", "num": 42}}}),

    ("signal_multiple_receivers", """
import blinker
sig = blinker.Signal()
def handler1(sender):
    return 'result1'
def handler2(sender):
    return 'result2'
sig.connect(handler1, weak=False)
sig.connect(handler2, weak=False)
results = sig.send('sender')
result = {"count": len(results), "values": sorted([r[1] for r in results])}
""", {"ok": True, "value": {"count": 2, "values": ["result1", "result2"]}}),

    ("signal_receiver_order", """
import blinker
sig = blinker.Signal()
order = []
def handler1(sender):
    order.append(1)
    return 1
def handler2(sender):
    order.append(2)
    return 2
def handler3(sender):
    order.append(3)
    return 3
sig.connect(handler1, weak=False)
sig.connect(handler2, weak=False)
sig.connect(handler3, weak=False)
sig.send('sender')
result = {"received_all": len(order) == 3}
""", {"ok": True, "value": {"received_all": True}}),

    # Sender-specific connections
    ("signal_specific_sender", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return sender
sig.connect(handler, sender='specific', weak=False)
results = sig.send('specific')
result = {"count": len(results), "value": results[0][1] if results else None}
""", {"ok": True, "value": {"count": 1, "value": "specific"}}),

    ("signal_wrong_sender", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return sender
sig.connect(handler, sender='specific', weak=False)
results = sig.send('other')
result = {"count": len(results)}
""", {"ok": True, "value": {"count": 0}}),

    ("signal_any_sender", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'any'
sig.connect(handler, sender=blinker.ANY, weak=False)
r1 = sig.send('sender1')
r2 = sig.send('sender2')
result = {"r1_count": len(r1), "r2_count": len(r2)}
""", {"ok": True, "value": {"r1_count": 1, "r2_count": 1}}),

    ("signal_mixed_senders", """
import blinker
sig = blinker.Signal()
def handler_any(sender):
    return 'any'
def handler_specific(sender):
    return 'specific'
sig.connect(handler_any, sender=blinker.ANY, weak=False)
sig.connect(handler_specific, sender='target', weak=False)
results = sig.send('target')
result = {"count": len(results), "values": sorted([r[1] for r in results])}
""", {"ok": True, "value": {"count": 2, "values": ["any", "specific"]}}),

    # Disconnect
    ("signal_disconnect", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'test'
sig.connect(handler, weak=False)
sig.disconnect(handler)
results = sig.send('sender')
result = {"count": len(results)}
""", {"ok": True, "value": {"count": 0}}),

    ("signal_disconnect_specific_sender", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'test'
sig.connect(handler, sender='s1', weak=False)
sig.connect(handler, sender='s2', weak=False)
sig.disconnect(handler, sender='s1')
r1 = sig.send('s1')
r2 = sig.send('s2')
result = {"s1_count": len(r1), "s2_count": len(r2)}
""", {"ok": True, "value": {"s1_count": 0, "s2_count": 1}}),

    ("signal_disconnect_any", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'test'
sig.connect(handler, sender='s1', weak=False)
sig.connect(handler, sender='s2', weak=False)
sig.disconnect(handler)
r1 = sig.send('s1')
r2 = sig.send('s2')
result = {"s1_count": len(r1), "s2_count": len(r2)}
""", {"ok": True, "value": {"s1_count": 0, "s2_count": 0}}),

    # has_receivers_for
    ("has_receivers_empty", """
import blinker
sig = blinker.Signal()
result = sig.has_receivers_for('sender')
""", {"ok": True, "value": False}),

    ("has_receivers_any", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: None, sender=blinker.ANY, weak=False)
result = sig.has_receivers_for('anything')
""", {"ok": True, "value": True}),

    ("has_receivers_specific", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: None, sender='target', weak=False)
result = {"target": sig.has_receivers_for('target'), "other": sig.has_receivers_for('other')}
""", {"ok": True, "value": {"target": True, "other": False}}),

    ("has_receivers_check_any_sender", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: None, sender='specific', weak=False)
result = sig.has_receivers_for(blinker.ANY)
""", {"ok": True, "value": False}),

    # receivers_for
    ("receivers_for_empty", """
import blinker
sig = blinker.Signal()
receivers = list(sig.receivers_for('sender'))
result = {"count": len(receivers)}
""", {"ok": True, "value": {"count": 0}}),

    ("receivers_for_specific", """
import blinker
sig = blinker.Signal()
def handler(sender):
    pass
sig.connect(handler, sender='target', weak=False)
receivers = list(sig.receivers_for('target'))
result = {"count": len(receivers), "is_handler": receivers[0] is handler if receivers else False}
""", {"ok": True, "value": {"count": 1, "is_handler": True}}),

    ("receivers_for_any", """
import blinker
sig = blinker.Signal()
def handler(sender):
    pass
sig.connect(handler, sender=blinker.ANY, weak=False)
receivers = list(sig.receivers_for('anything'))
result = {"count": len(receivers)}
""", {"ok": True, "value": {"count": 1}}),

    ("receivers_for_mixed", """
import blinker
sig = blinker.Signal()
def handler_any(sender):
    pass
def handler_specific(sender):
    pass
sig.connect(handler_any, sender=blinker.ANY, weak=False)
sig.connect(handler_specific, sender='target', weak=False)
receivers = list(sig.receivers_for('target'))
result = {"count": len(receivers)}
""", {"ok": True, "value": {"count": 2}}),

    # connect_via decorator
    ("connect_via_basic", """
import blinker
sig = blinker.Signal()
@sig.connect_via('sender1', weak=False)
def handler(sender):
    return 'decorated'
results = sig.send('sender1')
result = {"count": len(results), "value": results[0][1] if results else None}
""", {"ok": True, "value": {"count": 1, "value": "decorated"}}),

    ("connect_via_any", """
import blinker
sig = blinker.Signal()
@sig.connect_via(blinker.ANY, weak=False)
def handler(sender):
    return sender
r1 = sig.send('s1')
r2 = sig.send('s2')
result = {"r1": r1[0][1], "r2": r2[0][1]}
""", {"ok": True, "value": {"r1": "s1", "r2": "s2"}}),

    # connected_to context manager
    ("connected_to_context", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'temp'
with sig.connected_to(handler):
    r_inside = sig.send('sender')
r_outside = sig.send('sender')
result = {"inside": len(r_inside), "outside": len(r_outside)}
""", {"ok": True, "value": {"inside": 1, "outside": 0}}),

    ("connected_to_specific_sender", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'temp'
with sig.connected_to(handler, sender='target'):
    r1 = sig.send('target')
    r2 = sig.send('other')
result = {"target": len(r1), "other": len(r2)}
""", {"ok": True, "value": {"target": 1, "other": 0}}),

    # muted context manager
    ("muted_context", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: 'test', weak=False)
r1 = sig.send('sender')
with sig.muted():
    r2 = sig.send('sender')
r3 = sig.send('sender')
result = {"before": len(r1), "during": len(r2), "after": len(r3)}
""", {"ok": True, "value": {"before": 1, "during": 0, "after": 1}}),

    ("muted_nested", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: 'test', weak=False)
with sig.muted():
    with sig.muted():
        r1 = sig.send('sender')
    r2 = sig.send('sender')
result = {"inner": len(r1), "outer": len(r2)}
""", {"ok": True, "value": {"inner": 0, "outer": 1}}),

    # Named signals and Namespace
    ("named_signal_basic", """
import blinker
sig = blinker.signal('test_signal')
result = {"type": type(sig).__name__, "name": sig.name}
""", {"ok": True, "value": {"type": "NamedSignal", "name": "test_signal"}}),

    ("named_signal_singleton", """
import blinker
sig1 = blinker.signal('my_signal')
sig2 = blinker.signal('my_signal')
result = sig1 is sig2
""", {"ok": True, "value": True}),

    ("named_signal_different", """
import blinker
sig1 = blinker.signal('signal1')
sig2 = blinker.signal('signal2')
result = sig1 is sig2
""", {"ok": True, "value": False}),

    ("named_signal_connect_send", """
import blinker
sig = blinker.signal('test')
sig.connect(lambda s: 'result', weak=False)
results = sig.send('sender')
result = {"count": len(results)}
""", {"ok": True, "value": {"count": 1}}),

    ("namespace_basic", """
import blinker
ns = blinker.Namespace()
sig = ns.signal('test')
result = {"type": type(sig).__name__, "name": sig.name}
""", {"ok": True, "value": {"type": "NamedSignal", "name": "test"}}),

    ("namespace_singleton", """
import blinker
ns = blinker.Namespace()
sig1 = ns.signal('sig')
sig2 = ns.signal('sig')
result = sig1 is sig2
""", {"ok": True, "value": True}),

    ("namespace_isolation", """
import blinker
ns1 = blinker.Namespace()
ns2 = blinker.Namespace()
sig1 = ns1.signal('test')
sig2 = ns2.signal('test')
result = sig1 is sig2
""", {"ok": True, "value": False}),

    ("default_namespace", """
import blinker
result = type(blinker.default_namespace).__name__
""", {"ok": True, "value": "Namespace"}),

    # Weak references
    ("weak_reference_default", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'test'
sig.connect(handler)
result = {"has_receivers": sig.has_receivers_for('sender')}
""", {"ok": True, "value": {"has_receivers": True}}),

    ("strong_reference", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'test'
sig.connect(handler, weak=False)
result = {"has_receivers": sig.has_receivers_for('sender')}
""", {"ok": True, "value": {"has_receivers": True}}),

    # receiver_connected signal
    ("receiver_connected_signal", """
import blinker
sig = blinker.Signal()
connected_calls = []
def on_connect(signal_sender, **kwargs):
    connected_calls.append((signal_sender, kwargs.get('receiver'), kwargs.get('sender')))
sig.receiver_connected.connect(on_connect, weak=False)
def handler(s):
    pass
sig.connect(handler, sender='target', weak=False)
result = {"count": len(connected_calls), "signal_is_sender": connected_calls[0][0] is sig if connected_calls else False}
""", {"ok": True, "value": {"count": 1, "signal_is_sender": True}}),

    # receiver_disconnected signal
    ("receiver_disconnected_signal", """
import blinker
sig = blinker.Signal()
disconnected_calls = []
def on_disconnect(signal_sender, **kwargs):
    disconnected_calls.append((signal_sender, kwargs.get('receiver')))
sig.receiver_disconnected.connect(on_disconnect, weak=False)
def handler(s):
    pass
sig.connect(handler, weak=False)
sig.disconnect(handler)
result = {"count": len(disconnected_calls)}
""", {"ok": True, "value": {"count": 1}}),

    # ANY symbol
    ("any_symbol", """
import blinker
result = {"type": type(blinker.ANY).__name__, "repr": repr(blinker.ANY)}
""", {"ok": True, "value": {"type": "Symbol", "repr": "ANY"}}),

    ("any_via_signal", """
import blinker
sig = blinker.Signal()
result = sig.ANY is blinker.ANY
""", {"ok": True, "value": True}),

    # receivers attribute
    ("receivers_attribute_empty", """
import blinker
sig = blinker.Signal()
result = {"bool": bool(sig.receivers)}
""", {"ok": True, "value": {"bool": False}}),

    ("receivers_attribute_nonempty", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: None, weak=False)
result = {"bool": bool(sig.receivers)}
""", {"ok": True, "value": {"bool": True}}),

    # Return value handling
    ("receiver_return_none", """
import blinker
sig = blinker.Signal()
def handler(sender):
    pass
sig.connect(handler, weak=False)
results = sig.send('sender')
result = {"value": results[0][1]}
""", {"ok": True, "value": {"value": None}}),

    ("receiver_return_string", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'test_string'
sig.connect(handler, weak=False)
results = sig.send('sender')
result = {"value": results[0][1]}
""", {"ok": True, "value": {"value": "test_string"}}),

    ("receiver_return_number", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 42
sig.connect(handler, weak=False)
results = sig.send('sender')
result = {"value": results[0][1]}
""", {"ok": True, "value": {"value": 42}}),

    ("receiver_return_list", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return [1, 2, 3]
sig.connect(handler, weak=False)
results = sig.send('sender')
result = {"value": results[0][1]}
""", {"ok": True, "value": {"value": [1, 2, 3]}}),

    ("receiver_return_dict", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return {"key": "value"}
sig.connect(handler, weak=False)
results = sig.send('sender')
result = {"value": results[0][1]}
""", {"ok": True, "value": {"value": {"key": "value"}}}),

    # Multiple connections of same receiver
    ("same_receiver_different_senders", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return sender
sig.connect(handler, sender='s1', weak=False)
sig.connect(handler, sender='s2', weak=False)
r1 = sig.send('s1')
r2 = sig.send('s2')
result = {"r1_count": len(r1), "r2_count": len(r2)}
""", {"ok": True, "value": {"r1_count": 1, "r2_count": 1}}),

    ("same_receiver_any_and_specific", """
import blinker
sig = blinker.Signal()
call_count = [0]
def handler(sender):
    call_count[0] += 1
    return 'test'
sig.connect(handler, sender=blinker.ANY, weak=False)
sig.connect(handler, sender='specific', weak=False)
results = sig.send('specific')
result = {"result_count": len(results), "call_count": call_count[0]}
""", {"ok": True, "value": {"result_count": 1, "call_count": 1}}),

    # Edge cases
    ("send_none_sender", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: s, weak=False)
results = sig.send(None)
result = {"count": len(results), "sender": results[0][1]}
""", {"ok": True, "value": {"count": 1, "sender": None}}),

    ("send_with_no_kwargs", """
import blinker
sig = blinker.Signal()
received = []
def handler(sender, **kwargs):
    received.append(kwargs)
sig.connect(handler, weak=False)
sig.send('sender')
result = {"kwargs": received[0]}
""", {"ok": True, "value": {"kwargs": {}}}),

    ("receiver_uses_kwargs", """
import blinker
sig = blinker.Signal()
def handler(sender, **kwargs):
    return kwargs.get('value', 'default')
sig.connect(handler, weak=False)
r1 = sig.send('sender', value='custom')
r2 = sig.send('sender')
result = {"with_value": r1[0][1], "without_value": r2[0][1]}
""", {"ok": True, "value": {"with_value": "custom", "without_value": "default"}}),

    ("empty_send_returns_empty_list", """
import blinker
sig = blinker.Signal()
results = sig.send('sender')
result = {"type": type(results).__name__, "len": len(results)}
""", {"ok": True, "value": {"type": "list", "len": 0}}),

    ("send_returns_list_of_tuples", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: 'a', weak=False)
sig.connect(lambda s: 'b', weak=False)
results = sig.send('sender')
result = {"is_list": isinstance(results, list), "len": len(results), "is_tuple": all(isinstance(r, tuple) for r in results)}
""", {"ok": True, "value": {"is_list": True, "len": 2, "is_tuple": True}}),

    ("tuple_structure", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'value'
sig.connect(handler, weak=False)
results = sig.send('sender')
result = {"tuple_len": len(results[0]), "has_callable": callable(results[0][0]), "value": results[0][1]}
""", {"ok": True, "value": {"tuple_len": 2, "has_callable": True, "value": "value"}}),

    # Signal with doc
    ("signal_with_doc", """
import blinker
sig = blinker.Signal(doc='Test documentation')
result = {"has_doc": sig.__doc__ == 'Test documentation'}
""", {"ok": True, "value": {"has_doc": True}}),

    ("named_signal_with_doc", """
import blinker
ns = blinker.Namespace()
sig = ns.signal('test', doc='Test doc')
result = {"has_doc": sig.__doc__ == 'Test doc', "name": sig.name}
""", {"ok": True, "value": {"has_doc": True, "name": "test"}}),

    # Complex scenario
    ("complex_multi_sender_receiver", """
import blinker
sig = blinker.Signal()
results_log = []
def handler1(sender, **kwargs):
    results_log.append(('h1', sender, kwargs.get('val')))
    return 'h1_result'
def handler2(sender, **kwargs):
    results_log.append(('h2', sender, kwargs.get('val')))
    return 'h2_result'
sig.connect(handler1, sender='s1', weak=False)
sig.connect(handler2, sender='s2', weak=False)
sig.connect(handler1, sender=blinker.ANY, weak=False)
r1 = sig.send('s1', val='v1')
r2 = sig.send('s2', val='v2')
result = {"r1_count": len(r1), "r2_count": len(r2), "log_count": len(results_log)}
""", {"ok": True, "value": {"r1_count": 1, "r2_count": 2, "log_count": 3}}),

    ("multiple_sends", """
import blinker
sig = blinker.Signal()
counter = [0]
def handler(sender):
    counter[0] += 1
    return counter[0]
sig.connect(handler, weak=False)
r1 = sig.send('s1')
r2 = sig.send('s2')
r3 = sig.send('s3')
result = {"r1": r1[0][1], "r2": r2[0][1], "r3": r3[0][1]}
""", {"ok": True, "value": {"r1": 1, "r2": 2, "r3": 3}}),

    # Disconnect scenarios
    ("disconnect_nonexistent", """
import blinker
sig = blinker.Signal()
def handler(sender):
    pass
sig.disconnect(handler)
result = {"success": True}
""", {"ok": True, "value": {"success": True}}),

    ("disconnect_after_multiple_connects", """
import blinker
sig = blinker.Signal()
def handler(sender):
    return 'test'
sig.connect(handler, sender='s1', weak=False)
sig.connect(handler, sender='s2', weak=False)
sig.connect(handler, sender='s3', weak=False)
sig.disconnect(handler, sender='s2')
r1 = sig.send('s1')
r2 = sig.send('s2')
r3 = sig.send('s3')
result = {"r1": len(r1), "r2": len(r2), "r3": len(r3)}
""", {"ok": True, "value": {"r1": 1, "r2": 0, "r3": 1}}),

    # Connect return value
    ("connect_returns_receiver", """
import blinker
sig = blinker.Signal()
def handler(sender):
    pass
returned = sig.connect(handler, weak=False)
result = returned is handler
""", {"ok": True, "value": True}),

    # Receiver with positional sender
    ("receiver_positional_sender", """
import blinker
sig = blinker.Signal()
received_sender = []
def handler(sender):
    received_sender.append(sender)
    return 'ok'
sig.connect(handler, weak=False)
sig.send('my_sender')
result = {"sender": received_sender[0]}
""", {"ok": True, "value": {"sender": "my_sender"}}),

    # Multiple named signals
    ("multiple_named_signals_isolation", """
import blinker
sig1 = blinker.signal('sig1')
sig2 = blinker.signal('sig2')
sig1.connect(lambda s: 'r1', weak=False)
sig2.connect(lambda s: 'r2', weak=False)
r1 = sig1.send('sender')
r2 = sig2.send('sender')
result = {"r1_val": r1[0][1], "r2_val": r2[0][1]}
""", {"ok": True, "value": {"r1_val": "r1", "r2_val": "r2"}}),

    ("namespace_dict_access", """
import blinker
ns = blinker.Namespace()
sig1 = ns.signal('test')
sig2 = ns['test']
result = sig1 is sig2
""", {"ok": True, "value": True}),

    # Lambda receivers
    ("lambda_receiver", """
import blinker
sig = blinker.Signal()
sig.connect(lambda s: 'lambda_result', weak=False)
results = sig.send('sender')
result = {"count": len(results), "value": results[0][1]}
""", {"ok": True, "value": {"count": 1, "value": "lambda_result"}}),

    # Receiver modifying shared state
    ("receiver_shared_state", """
import blinker
sig = blinker.Signal()
state = {'counter': 0}
def handler(sender, **kwargs):
    state['counter'] += 1
sig.connect(handler, weak=False)
sig.send('s1')
sig.send('s2')
sig.send('s3')
result = {"counter": state['counter']}
""", {"ok": True, "value": {"counter": 3}}),

    # Chaining signals
    ("signal_chain", """
import blinker
sig1 = blinker.Signal()
sig2 = blinker.Signal()
def relay(sender, **kwargs):
    sig2.send(sender, **kwargs)
sig1.connect(relay, weak=False)
results = []
def final_handler(sender, **kwargs):
    results.append((sender, kwargs))
sig2.connect(final_handler, weak=False)
sig1.send('origin', key='value')
result = {"count": len(results), "sender": results[0][0], "key": results[0][1].get('key')}
""", {"ok": True, "value": {"count": 1, "sender": "origin", "key": "value"}}),
]

def main():
    """Run all test cases and output JSON result."""
    leaves = []
    for test_id, script, expected in CASES:
        actual = execute_script(script)
        if actual == expected:
            status = "passed"
        else:
            status = "failed"
        leaves.append({"id": test_id, "status": status})
    
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))
    return 0

if __name__ == "__main__":
    sys.exit(main())
