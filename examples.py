def print_in_while(a):
    try:
        while a > 0:
            print('a = {}'.format(a))
            a -= 1
            if a == 7:
                return None
    finally:
        print('The end!')


def print_in_while_return(a):
    while a > 0:
        print('a = {}'.format(a))
        a -= 1
        if a == 7:
            return None


if __name__ == '__main__':
    print_in_while(15)

    print_in_while_return(15)
