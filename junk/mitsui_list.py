def main():
    import sys
    import json

    f = sys.argv[1]

    for line in open(f):
        data = json.loads(line)
        node = data['node_name']
        print node


if __name__ == '__main__':
    main()
