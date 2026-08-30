# Run Rust proof alongside the Java vertical slice

After the shared F0, F0.5, and F1 gates pass, the synthetic Rust proof may run alongside the Java vertical slice so language bias in the shared contracts is exposed early. The Rust production lane remains blocked until the Java pilot passes, preserving the stronger production-risk gate while allowing independent adapter work to proceed.
