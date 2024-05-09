import os, sys
rp = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(rp)
sys.path.append(os.path.join(rp, 'helper', 'resolveurl', 'lib'))
sys.path.append(os.path.join(rp, 'helper', 'sites'))
sys.path.append(os.path.join(rp, 'helper'))
sys.path.append(os.path.join(rp, 'utils'))
import utils.common as com
com.check()

import cli, services


def main():
    services.handler('init')
    cli.menu()
    sys.exit(0)


if __name__ == "__main__":
    main()
