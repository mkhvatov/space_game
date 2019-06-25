def print_in_while(a):
    try:
        while a > 0:
            print('a = {}'.format(a))
            a -= 1
    finally:
        print('The end!')


if __name__ == '__main__':
    print_in_while(10)
