#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/reflections/util src/main/java/org/reflections
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/reflections/ReflectionsException.java <<'JAVA'
package org.reflections;
public class ReflectionsException extends RuntimeException { public ReflectionsException(String message){super(message);} public ReflectionsException(String message, Throwable cause){super(message,cause);} public ReflectionsException(Throwable cause){super(cause);} }
JAVA
cat > src/main/java/org/reflections/util/FilterBuilder.java <<'JAVA'
package org.reflections.util;
import java.util.*;
import java.util.function.Predicate;
import java.util.regex.Pattern;
import org.reflections.ReflectionsException;
public class FilterBuilder implements Predicate<String> {
 private final List<Predicate<String>> chain = new ArrayList<>();
 public FilterBuilder() {}
 public FilterBuilder includePackage(String value){return includePattern(prefixPattern(value));}
 public FilterBuilder excludePackage(String value){return excludePattern(prefixPattern(value));}
 public FilterBuilder includePattern(String regex){return add(new Include(regex));}
 public FilterBuilder excludePattern(String regex){return add(new Exclude(regex));}
 @Deprecated public FilterBuilder include(String regex){return add(new Include(regex));}
 @Deprecated public FilterBuilder exclude(String regex){return add(new Exclude(regex));}
 public static FilterBuilder parsePackages(String input){List<Predicate<String>> filters=new ArrayList<>(); for(String value:input.split(",")){String trimmed=value.trim(); char prefix=trimmed.charAt(0); String pattern=prefixPattern(trimmed.substring(1)); switch(prefix){case '+':filters.add(new Include(pattern));break;case '-':filters.add(new Exclude(pattern));break;default:throw new ReflectionsException("includeExclude should start with either + or -");}} return new FilterBuilder(filters);}
 private FilterBuilder(Collection<Predicate<String>> filters){chain.addAll(filters);}
 public FilterBuilder add(Predicate<String> filter){chain.add(filter);return this;}
 public boolean test(String value){boolean accept=chain.isEmpty()||chain.get(0) instanceof Exclude; for(Predicate<String> filter:chain){if(accept&&filter instanceof Include)continue; if(!accept&&filter instanceof Exclude)continue; accept=filter.test(value); if(!accept&&filter instanceof Exclude)break;}return accept;}
 private static String prefixPattern(String value){if(!value.endsWith("."))value += ".";return value.replace(".","\\.").replace("$","\\$")+".*";}
 abstract static class Matcher implements Predicate<String>{final Pattern pattern; Matcher(String regex){pattern=Pattern.compile(regex);}}
 static class Include extends Matcher{Include(String regex){super(regex);}public boolean test(String value){return pattern.matcher(value).matches();}}
 static class Exclude extends Matcher{Exclude(String regex){super(regex);}public boolean test(String value){return !pattern.matcher(value).matches();}}
}
JAVA
