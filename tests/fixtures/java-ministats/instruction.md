# Build a Java text utility

Create a Maven-compatible Java project with the public class
`example.text.TextUtil` and the public static method
`String normalize(String value)`. The method removes surrounding ASCII
whitespace and returns the normalized string. A null input must return null.

The project must compile on the locked JDK 21 runtime, use no network access,
and keep all implementation under `src/main/java`.
