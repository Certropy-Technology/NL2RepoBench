# Build a Java text utility

Create a Maven-compatible Java project with the public class
`example.text.TextUtil` and the public static method
`String normalize(String value)`. The method removes surrounding ASCII
whitespace and returns the normalized string. A null input must return null.

The project must compile on JDK 21, use the supplied Maven project shape, and
keep implementation under `src/main/java`. Do not add build plugins, external
repositories, generated binaries, or executable files.
