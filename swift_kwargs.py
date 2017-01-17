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
            one_character=0,
        ),
        non_matching_contents=set(),
    )


def process_line(l):
    # print(l)
    if 'var ' in l or 'func ' in l:
        return 0, 0, 0
    m = 0
    n_m = 0
    p = 0
    oc = 0
    for match in re.finditer('[(\s](?P<name>\w+):\s*(?P<value>\w+)', l):
        name, value = match.groups()
        if name == value:
            m += 1
        elif name.lower() in value.lower():
            p += 1
        elif value.lower() == name[0].lower():
            oc += 1
        else:
            # if len(value) == 1:
            #     print(name, value)
            n_m += 1
            # if value == 'Int':
            #     print(l)
            #     exit(1)
            results.non_matching_contents.add((name, value))
    results.buckets.matching += m
    results.buckets.non_matching += n_m
    results.buckets.partial += p
    results.buckets.one_character += oc
    return m, n_m, p
        
# reset()
# assert process_line('foo(bar:bar, baz: baz, quux:1, qwe:qwe_1)') == (2, 1, 1)


def stats(filename):
    with open(filename, encoding='utf8') as f:
        try:
            contents = re.sub('(func|var)\w.*?{', '', f.read(), flags=re.MULTILINE)
            for l in contents.split('\n'):
                process_line(l)
        except UnicodeDecodeError as e:
            print('failed to parse %s: %s' % (filename, e))


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
    # print('--- %s ---' % directory)
    for root, dirs, files in os.walk(directory):
        for f in files:
            if not f.endswith('.swift'):
                continue
                
            p = os.path.join(root, f)
            stats(p)
    # print_results()


reset()
print('name,', ', '.join([k for k in results.buckets.keys()]))

for d in os.listdir('repos/'):
    if not os.path.isdir('repos/%s' % d):
        continue

    for d2 in os.listdir('repos/%s' % d):
        main('repos/%s/%s' % (d, d2))
        print('%s,' % d2, ', '.join([str(k) for k in results.buckets.values()]))
