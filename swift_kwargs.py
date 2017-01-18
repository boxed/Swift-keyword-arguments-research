import os
import re
from tri.struct import Struct

results = None


def reset():
    global results
    results = Struct(
        buckets=Struct(
            matching=0,
            non_matching=0,
            partial=0,
            one_char_prefix=0,
            one_char=0,
        ),
        non_matching_contents=set(),
    )


def process_line(l):
    # print(l)
    if 'var ' in l or 'func ' in l:
        return

    for match in re.finditer('[(\s](?P<name>\w+):\s*(?P<value>\w+)', l):
        name, value = match.groups()

        try:
            int(value)
            is_digit = True
        except ValueError:
            is_digit = False

        if name == value:
            results.buckets.matching += 1
        elif name.lower() in value.lower():
            results.buckets.partial += 1
        elif value.lower() == name[0].lower():
            results.buckets.one_char_prefix += 1
        elif len(value) == 1 and not is_digit:
            results.buckets.one_char += 1
        else:
            # if len(value) == 1:
            #     print(name, value)
            results.buckets.non_matching += 1
            # if value == 'Int':
            #     print(l)
            #     exit(1)
            results.non_matching_contents.add((name, value))


def stats(filename):
    with open(filename, encoding='utf8') as f:
        try:
            contents = re.sub('(func|var)\w.*?{', '', f.read(), flags=re.MULTILINE)
            for l in contents.split('\n'):
                process_line(l)
        except UnicodeDecodeError as e:
            # print('failed to parse %s: %s' % (filename, e))
            pass


def print_results():
    total = sum(results.buckets.values())
    for k, v in results.buckets.items():
        print('%s:' % k, v, '(%.2f%%)' % (v / total * 100))
    # print(len(results.non_matching_contents))
    # for x in sorted(results.non_matching_contents):
        # print(x)


def main(directory):
    if not os.path.isdir(directory):
        return

    reset()

    for root, dirs, files in os.walk(directory):
        for f in files:
            if not f.endswith('.swift'):
                continue
                
            p = os.path.join(root, f)
            stats(p)


reset()

for d in os.listdir('repos/'):
    if not os.path.isdir('repos/%s' % d):
        continue

    print()
    print(d)
    print()
    print('name |', ' | '.join([k for k in results.buckets.keys()]), '| total')
    print('---- |', ' | '.join(['-' * len(k) for k in results.buckets.keys()]), '| ------------------')

    for d2 in os.listdir('repos/%s' % d):
        if not os.path.isdir('repos/%s/%s' % (d, d2)):
            continue

        main('repos/%s/%s' % (d, d2))
        total = sum(results.buckets.values())
        print('%s |' % d2, ' | '.join(['%s (%.2f%%)' % (v, v * 100 / total) for v in results.buckets.values()]), '|', total)
