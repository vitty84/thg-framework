from lib.base import THGBASECONSOLE


class THGSTART(THGBASECONSOLE):
    def run(self):
        self.cmdloop()

if __name__ == '__main__':
    thg = THGSTART()
    thg.run()
