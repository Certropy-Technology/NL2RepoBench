#!/usr/bin/env python3
"""Verifier for inflect library task."""
import json
import sys
from nl2repobench.verification.candidate_client import execute_script

CASES = [
    # === Basic plural/singular transformations ===
    ("plural_cat", "import inflect\np = inflect.engine()\nresult = p.plural('cat')", {"ok": True, "value": "cats"}),
    ("plural_dog", "import inflect\np = inflect.engine()\nresult = p.plural('dog')", {"ok": True, "value": "dogs"}),
    ("plural_person", "import inflect\np = inflect.engine()\nresult = p.plural('person')", {"ok": True, "value": "people"}),
    ("plural_child", "import inflect\np = inflect.engine()\nresult = p.plural('child')", {"ok": True, "value": "children"}),
    ("plural_knife", "import inflect\np = inflect.engine()\nresult = p.plural('knife')", {"ok": True, "value": "knives"}),
    ("plural_box", "import inflect\np = inflect.engine()\nresult = p.plural('box')", {"ok": True, "value": "boxes"}),
    ("plural_mouse", "import inflect\np = inflect.engine()\nresult = p.plural('mouse')", {"ok": True, "value": "mice"}),
    ("plural_foot", "import inflect\np = inflect.engine()\nresult = p.plural('foot')", {"ok": True, "value": "feet"}),
    ("plural_tooth", "import inflect\np = inflect.engine()\nresult = p.plural('tooth')", {"ok": True, "value": "teeth"}),
    ("plural_goose", "import inflect\np = inflect.engine()\nresult = p.plural('goose')", {"ok": True, "value": "geese"}),
    
    # === Singular noun (plural to singular) ===
    ("singular_cats", "import inflect\np = inflect.engine()\nresult = p.singular_noun('cats')", {"ok": True, "value": "cat"}),
    ("singular_dogs", "import inflect\np = inflect.engine()\nresult = p.singular_noun('dogs')", {"ok": True, "value": "dog"}),
    ("singular_people", "import inflect\np = inflect.engine()\nresult = p.singular_noun('people')", {"ok": True, "value": "person"}),
    ("singular_children", "import inflect\np = inflect.engine()\nresult = p.singular_noun('children')", {"ok": True, "value": "child"}),
    ("singular_knives", "import inflect\np = inflect.engine()\nresult = p.singular_noun('knives')", {"ok": True, "value": "knife"}),
    ("singular_mice", "import inflect\np = inflect.engine()\nresult = p.singular_noun('mice')", {"ok": True, "value": "mouse"}),
    ("singular_feet", "import inflect\np = inflect.engine()\nresult = p.singular_noun('feet')", {"ok": True, "value": "foot"}),
    ("singular_teeth", "import inflect\np = inflect.engine()\nresult = p.singular_noun('teeth')", {"ok": True, "value": "tooth"}),
    
    # === Plural with count (conditional plurals) ===
    ("plural_count_1", "import inflect\np = inflect.engine()\nresult = p.plural('cat', 1)", {"ok": True, "value": "cat"}),
    ("plural_count_2", "import inflect\np = inflect.engine()\nresult = p.plural('cat', 2)", {"ok": True, "value": "cats"}),
    ("plural_count_0", "import inflect\np = inflect.engine()\nresult = p.plural('dog', 0)", {"ok": True, "value": "dogs"}),
    ("plural_count_5", "import inflect\np = inflect.engine()\nresult = p.plural('person', 5)", {"ok": True, "value": "people"}),
    
    # === A/an indefinite articles ===
    ("a_apple", "import inflect\np = inflect.engine()\nresult = p.a('apple')", {"ok": True, "value": "an apple"}),
    ("a_banana", "import inflect\np = inflect.engine()\nresult = p.a('banana')", {"ok": True, "value": "a banana"}),
    ("a_orange", "import inflect\np = inflect.engine()\nresult = p.a('orange')", {"ok": True, "value": "an orange"}),
    ("a_university", "import inflect\np = inflect.engine()\nresult = p.a('university')", {"ok": True, "value": "a university"}),
    ("a_hour", "import inflect\np = inflect.engine()\nresult = p.a('hour')", {"ok": True, "value": "an hour"}),
    ("an_apple", "import inflect\np = inflect.engine()\nresult = p.an('apple')", {"ok": True, "value": "an apple"}),
    ("an_banana", "import inflect\np = inflect.engine()\nresult = p.an('banana')", {"ok": True, "value": "a banana"}),
    
    # === Ordinals ===
    ("ordinal_1", "import inflect\np = inflect.engine()\nresult = p.ordinal(1)", {"ok": True, "value": "1st"}),
    ("ordinal_2", "import inflect\np = inflect.engine()\nresult = p.ordinal(2)", {"ok": True, "value": "2nd"}),
    ("ordinal_3", "import inflect\np = inflect.engine()\nresult = p.ordinal(3)", {"ok": True, "value": "3rd"}),
    ("ordinal_4", "import inflect\np = inflect.engine()\nresult = p.ordinal(4)", {"ok": True, "value": "4th"}),
    ("ordinal_11", "import inflect\np = inflect.engine()\nresult = p.ordinal(11)", {"ok": True, "value": "11th"}),
    ("ordinal_21", "import inflect\np = inflect.engine()\nresult = p.ordinal(21)", {"ok": True, "value": "21st"}),
    ("ordinal_22", "import inflect\np = inflect.engine()\nresult = p.ordinal(22)", {"ok": True, "value": "22nd"}),
    ("ordinal_23", "import inflect\np = inflect.engine()\nresult = p.ordinal(23)", {"ok": True, "value": "23rd"}),
    ("ordinal_100", "import inflect\np = inflect.engine()\nresult = p.ordinal(100)", {"ok": True, "value": "100th"}),
    ("ordinal_101", "import inflect\np = inflect.engine()\nresult = p.ordinal(101)", {"ok": True, "value": "101st"}),
    
    # === Number to words ===
    ("num_to_words_0", "import inflect\np = inflect.engine()\nresult = p.number_to_words(0)", {"ok": True, "value": "zero"}),
    ("num_to_words_1", "import inflect\np = inflect.engine()\nresult = p.number_to_words(1)", {"ok": True, "value": "one"}),
    ("num_to_words_5", "import inflect\np = inflect.engine()\nresult = p.number_to_words(5)", {"ok": True, "value": "five"}),
    ("num_to_words_13", "import inflect\np = inflect.engine()\nresult = p.number_to_words(13)", {"ok": True, "value": "thirteen"}),
    ("num_to_words_42", "import inflect\np = inflect.engine()\nresult = p.number_to_words(42)", {"ok": True, "value": "forty-two"}),
    ("num_to_words_99", "import inflect\np = inflect.engine()\nresult = p.number_to_words(99)", {"ok": True, "value": "ninety-nine"}),
    ("num_to_words_100", "import inflect\np = inflect.engine()\nresult = p.number_to_words(100)", {"ok": True, "value": "one hundred"}),
    ("num_to_words_256", "import inflect\np = inflect.engine()\nresult = p.number_to_words(256)", {"ok": True, "value": "two hundred and fifty-six"}),
    ("num_to_words_1000", "import inflect\np = inflect.engine()\nresult = p.number_to_words(1000)", {"ok": True, "value": "one thousand"}),
    ("num_to_words_1234", "import inflect\np = inflect.engine()\nresult = p.number_to_words(1234)", {"ok": True, "value": "one thousand, two hundred and thirty-four"}),
    
    # === No (count with word) ===
    ("no_error_0", "import inflect\np = inflect.engine()\nresult = p.no('error', 0)", {"ok": True, "value": "no errors"}),
    ("no_error_1", "import inflect\np = inflect.engine()\nresult = p.no('error', 1)", {"ok": True, "value": "1 error"}),
    ("no_error_2", "import inflect\np = inflect.engine()\nresult = p.no('error', 2)", {"ok": True, "value": "2 errors"}),
    ("no_error_5", "import inflect\np = inflect.engine()\nresult = p.no('error', 5)", {"ok": True, "value": "5 errors"}),
    ("no_cat_0", "import inflect\np = inflect.engine()\nresult = p.no('cat', 0)", {"ok": True, "value": "no cats"}),
    ("no_cat_1", "import inflect\np = inflect.engine()\nresult = p.no('cat', 1)", {"ok": True, "value": "1 cat"}),
    
    # === Compare (number-insensitive equality) ===
    ("compare_cat_cat", "import inflect\np = inflect.engine()\nresult = p.compare('cat', 'cat')", {"ok": True, "value": "eq"}),
    ("compare_cat_cats", "import inflect\np = inflect.engine()\nresult = p.compare('cat', 'cats')", {"ok": True, "value": "s:p"}),
    ("compare_cats_cat", "import inflect\np = inflect.engine()\nresult = p.compare('cats', 'cat')", {"ok": True, "value": "p:s"}),
    ("compare_person_people", "import inflect\np = inflect.engine()\nresult = p.compare('person', 'people')", {"ok": True, "value": "s:p"}),
    ("compare_people_persons", "import inflect\np = inflect.engine()\nresult = p.compare('people', 'persons')", {"ok": True, "value": False}),
    ("compare_dog_cat", "import inflect\np = inflect.engine()\nresult = p.compare('dog', 'cat')", {"ok": True, "value": False}),
    
    # === Join (list to string) ===
    ("join_2items", "import inflect\np = inflect.engine()\nresult = p.join(['apple', 'banana'])", {"ok": True, "value": "apple and banana"}),
    ("join_3items", "import inflect\np = inflect.engine()\nresult = p.join(['apple', 'banana', 'cherry'])", {"ok": True, "value": "apple, banana, and cherry"}),
    ("join_4items", "import inflect\np = inflect.engine()\nresult = p.join(['red', 'green', 'blue', 'yellow'])", {"ok": True, "value": "red, green, blue, and yellow"}),
    ("join_1item", "import inflect\np = inflect.engine()\nresult = p.join(['apple'])", {"ok": True, "value": "apple"}),
    
    # === Plural noun specific ===
    ("plural_noun_cat", "import inflect\np = inflect.engine()\nresult = p.plural_noun('cat')", {"ok": True, "value": "cats"}),
    ("plural_noun_I", "import inflect\np = inflect.engine()\nresult = p.plural_noun('I', 2)", {"ok": True, "value": "we"}),
    ("plural_noun_me", "import inflect\np = inflect.engine()\nresult = p.plural_noun('me', 2)", {"ok": True, "value": "us"}),
    ("plural_noun_mine", "import inflect\np = inflect.engine()\nresult = p.plural_noun('mine', 2)", {"ok": True, "value": "ours"}),
    
    # === Plural verb specific ===
    ("plural_verb_was_1", "import inflect\np = inflect.engine()\nresult = p.plural_verb('was', 1)", {"ok": True, "value": "was"}),
    ("plural_verb_was_2", "import inflect\np = inflect.engine()\nresult = p.plural_verb('was', 2)", {"ok": True, "value": "were"}),
    ("plural_verb_is_1", "import inflect\np = inflect.engine()\nresult = p.plural_verb('is', 1)", {"ok": True, "value": "is"}),
    ("plural_verb_is_2", "import inflect\np = inflect.engine()\nresult = p.plural_verb('is', 2)", {"ok": True, "value": "are"}),
    
    # === Plural adj specific ===
    ("plural_adj_my_1", "import inflect\np = inflect.engine()\nresult = p.plural_adj('my', 1)", {"ok": True, "value": "my"}),
    ("plural_adj_my_2", "import inflect\np = inflect.engine()\nresult = p.plural_adj('my', 2)", {"ok": True, "value": "our"}),
    ("plural_adj_this_1", "import inflect\np = inflect.engine()\nresult = p.plural_adj('this', 1)", {"ok": True, "value": "this"}),
    ("plural_adj_this_2", "import inflect\np = inflect.engine()\nresult = p.plural_adj('this', 2)", {"ok": True, "value": "these"}),
    ("plural_adj_that_2", "import inflect\np = inflect.engine()\nresult = p.plural_adj('that', 2)", {"ok": True, "value": "those"}),
    
    # === More complex plurals ===
    ("plural_woman", "import inflect\np = inflect.engine()\nresult = p.plural('woman')", {"ok": True, "value": "women"}),
    ("plural_man", "import inflect\np = inflect.engine()\nresult = p.plural('man')", {"ok": True, "value": "men"}),
    ("plural_sheep", "import inflect\np = inflect.engine()\nresult = p.plural('sheep')", {"ok": True, "value": "sheep"}),
    ("plural_fish", "import inflect\np = inflect.engine()\nresult = p.plural('fish')", {"ok": True, "value": "fish"}),
    ("plural_ox", "import inflect\np = inflect.engine()\nresult = p.plural('ox')", {"ok": True, "value": "oxen"}),
    ("plural_bus", "import inflect\np = inflect.engine()\nresult = p.plural('bus')", {"ok": True, "value": "buses"}),
    ("plural_glass", "import inflect\np = inflect.engine()\nresult = p.plural('glass')", {"ok": True, "value": "glasses"}),
    ("plural_quiz", "import inflect\np = inflect.engine()\nresult = p.plural('quiz')", {"ok": True, "value": "quizzes"}),
    
    # === Additional edge cases to reach 90 ===
    ("plural_life", "import inflect\np = inflect.engine()\nresult = p.plural('life')", {"ok": True, "value": "lives"}),
    ("plural_wife", "import inflect\np = inflect.engine()\nresult = p.plural('wife')", {"ok": True, "value": "wives"}),
    ("plural_city", "import inflect\np = inflect.engine()\nresult = p.plural('city')", {"ok": True, "value": "cities"}),
    ("singular_lives", "import inflect\np = inflect.engine()\nresult = p.singular_noun('lives')", {"ok": True, "value": "life"}),
]

assert len(CASES) == 90, f"Expected exactly 90 cases, got {len(CASES)}"

def main():
    leaves = []
    for test_id, script, expected in CASES:
        try:
            actual = execute_script(script)
            if actual == expected:
                leaves.append({"id": test_id, "status": "passed"})
            else:
                leaves.append({"id": test_id, "status": "failed"})
        except Exception as e:
            leaves.append({"id": test_id, "status": "failed"})
    
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))
    return 0

if __name__ == "__main__":
    sys.exit(main())
