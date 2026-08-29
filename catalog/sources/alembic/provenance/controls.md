# Control Evidence

The final compiled bundle was exercised through Harbor 0.21.0. Oracle passed all 20 frozen leaves with reward `1.0`. The separate verifier reported `public_network_available=false` and failed both `pypi.org:443` and `1.1.1.1:443` probes.

The empty workspace and installation-hang controls used the permitted `candidate-installation-failed` `0/0` result. Stub, forgery, and call-hang controls collected all 20 leaves and passed zero. The invalid-workspace control was rejected before candidate installation. All controls had `valid=true` and reward `0.0`; the source `production-evidence.json` binds their final run paths to the final bundle digest.
