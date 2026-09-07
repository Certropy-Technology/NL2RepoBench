#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/tools/jackson/core
cat > /workspace/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>jackson-core</artifactId><version>1.0.0</version></project>
XML
cat > /workspace/src/main/java/tools/jackson/core/JsonPointer.java <<'JAVA'
package tools.jackson.core;
import java.util.*;
public final class JsonPointer {
    private static final JsonPointer EMPTY = new JsonPointer("", null, -1, null);
    private final String text, property; private final int index; private final JsonPointer next;
    private JsonPointer(String text, String property, int index, JsonPointer next) { this.text=text; this.property=property; this.index=index; this.next=next; }
    public static JsonPointer compile(String expr) {
        if (expr == null || expr.isEmpty()) return EMPTY;
        if (expr.charAt(0) != '/') throw new IllegalArgumentException("Invalid input");
        List<String> parts = new ArrayList<>(); int start=1;
        for (int i=1; i<=expr.length(); i++) if (i==expr.length() || expr.charAt(i)=='/') { parts.add(decode(expr.substring(start,i))); start=i+1; }
        JsonPointer result=EMPTY; for (int i=parts.size()-1;i>=0;i--) { String p=parts.get(i); result=new JsonPointer(expr,p,parseIndex(p),result); }
        return result;
    }
    public static JsonPointer empty() { return EMPTY; }
    public int length() { return toString().length(); }
    public boolean matches() { return next == null; }
    public String getMatchingProperty() { return property; }
    public int getMatchingIndex() { return index; }
    public boolean mayMatchProperty() { return property != null; }
    public boolean mayMatchElement() { return index >= 0; }
    public JsonPointer tail() { return next; }
    public JsonPointer head() { if (this==EMPTY) return null; List<String> p=parts(); if(p.size()==1)return EMPTY; p.remove(p.size()-1); return compile(render(p)); }
    public boolean matchesProperty(String name) { return next != null && Objects.equals(property,name); }
    public JsonPointer matchProperty(String name) { return matchesProperty(name) ? next : null; }
    public boolean matchesElement(int value) { return value >= 0 && value == index; }
    public JsonPointer matchElement(int value) { return matchesElement(value) ? next : null; }
    public JsonPointer appendProperty(String value) { return value == null ? this : compile(toString()+"/"+escape(value)); }
    public JsonPointer appendIndex(int value) { if(value<0) throw new IllegalArgumentException("Negative index"); return compile(toString()+"/"+value); }
    @Override public String toString() { return text; }
    @Override public boolean equals(Object o) { return o instanceof JsonPointer p && text.equals(p.text); }
    @Override public int hashCode() { return text.hashCode(); }
    private List<String> parts() { List<String> r=new ArrayList<>(); for(JsonPointer p=this;p!=EMPTY;p=p.next) r.add(p.property); return r; }
    private static String render(List<String> p) { StringBuilder b=new StringBuilder(); for(String s:p)b.append('/').append(escape(s)); return b.toString(); }
    private static String decode(String s) { StringBuilder b=new StringBuilder(); for(int i=0;i<s.length();i++){char c=s.charAt(i); if(c=='~'&&i+1<s.length()){char n=s.charAt(i+1); if(n=='0'){b.append('~');i++;continue;} if(n=='1'){b.append('/');i++;continue;}} b.append(c);} return b.toString(); }
    private static String escape(String s) { return s.replace("~","~0").replace("/","~1"); }
    private static int parseIndex(String s) { if(s.isEmpty() || (s.length()>1&&s.charAt(0)=='0') || s.length()>10) return -1; for(int i=0;i<s.length();i++)if(!Character.isDigit(s.charAt(i)))return -1; try{long n=Long.parseLong(s);return n<=Integer.MAX_VALUE?(int)n:-1;}catch(NumberFormatException e){return -1;} }
}
JAVA
