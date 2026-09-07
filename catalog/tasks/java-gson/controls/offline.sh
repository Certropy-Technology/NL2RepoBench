#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/google/gson src/main/java/com/google/gson/annotations
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/com/google/gson/FieldNamingStrategy.java <<'JAVA'
package com.google.gson;
import java.lang.reflect.Field;
import java.util.Collections;
import java.util.List;
public interface FieldNamingStrategy { String translateName(Field f); default List<String> alternateNames(Field f) { return Collections.emptyList(); } }
JAVA
cat > src/main/java/com/google/gson/FieldNamingPolicy.java <<'JAVA'
package com.google.gson;
import java.lang.reflect.Field;
import java.util.Locale;
public enum FieldNamingPolicy implements FieldNamingStrategy {
 IDENTITY { public String translateName(Field f) { return f.getName(); } },
 UPPER_CAMEL_CASE { public String translateName(Field f) { return upper(f.getName()); } },
 UPPER_CAMEL_CASE_WITH_SPACES { public String translateName(Field f) { return upper(separate(f.getName(),' ')); } },
 UPPER_CASE_WITH_UNDERSCORES { public String translateName(Field f) { return separate(f.getName(),'_').toUpperCase(Locale.ENGLISH); } },
 LOWER_CASE_WITH_UNDERSCORES { public String translateName(Field f) { return separate(f.getName(),'_').toLowerCase(Locale.ENGLISH); } },
 LOWER_CASE_WITH_DASHES { public String translateName(Field f) { return separate(f.getName(),'-').toLowerCase(Locale.ENGLISH); } },
 LOWER_CASE_WITH_DOTS { public String translateName(Field f) { return separate(f.getName(),'.').toLowerCase(Locale.ENGLISH); } };
 static String separate(String n,char s) { StringBuilder b=new StringBuilder(); for(int i=0;i<n.length();i++){char c=n.charAt(i); if(Character.isUpperCase(c)&&b.length()!=0)b.append(s); b.append(c);} return b.toString(); }
 static String upper(String s) { for(int i=0;i<s.length();i++) if(Character.isLetter(s.charAt(i))) { char c=s.charAt(i); if(Character.isUpperCase(c)) return s; return i==0?Character.toString(Character.toUpperCase(c))+s.substring(1):s.substring(0,i)+Character.toUpperCase(c)+s.substring(i+1); } return s; }
 public abstract String translateName(Field f);
}
JAVA
cat > src/main/java/com/google/gson/annotations/SerializedName.java <<'JAVA'
package com.google.gson.annotations;
import java.lang.annotation.*;
@Documented @Retention(RetentionPolicy.RUNTIME) @Target({ElementType.FIELD, ElementType.METHOD})
public @interface SerializedName { String value(); String[] alternate() default {}; }
JAVA
