# NL2RepoBench Java/Maven Pilot

This is a separate Java/Maven pilot release. Its task versions, source
revisions, Harbor bundle digests, Oracle receipts, and controls are independent
of the existing Python, Node, Go, and historical Harbor datasets.

The three tasks have current Oracle and controls evidence and passed
independent specification/security review. The bounded two-model pilot is
complete: Sol produced a candidate that passed the current verifier at 9/9;
Opus completed with a controlled model failure because it added forbidden
candidate-owned Maven build/plugins. The Java and OpenHands runtimes are built
from repository Dockerfiles with pinned upstream inputs. No private image
registry is required.
