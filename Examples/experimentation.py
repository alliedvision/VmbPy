from typing import get_type_hints

class VerifyTypeHints:
    def __init__(self):
        pass

    def __call__(self, func):
        hints = get_type_hints(func)

        def decorate(*args, **kwargs):
            for hint_name, hint_type in hints.items():
                print(hint_name, hint_type)

            #for k, w in kwargs.items():
            #    print(k, w)

            return func(*args, **kwargs)

        return decorate

@VerifyTypeHints()
def func(arg1: str):
    print('arg1={}, type(arg1)={}'.format(arg1, type(arg1)))

def main():
    func(1)

if __name__ == '__main__':
    main()
