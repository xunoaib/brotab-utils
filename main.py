from brotab_core import (bt_active, bt_list, move_tabs_to_window, spawn_window,
                         tabs_by_domain)


def move_domain_to_new_window(domain: str):
    '''Creates a new window and moves all tabs from the given domain to it'''

    tabs = bt_list()
    groups = tabs_by_domain(tabs)

    if ts := groups.get(domain, []):
        newtab = spawn_window()
        move_tabs_to_window(ts, newtab.window)
        newtab.close()


def print_tabs_by_group():
    tabs = bt_list()

    # groups = tabs_by_window(tabs)
    groups = tabs_by_domain(tabs)

    for key, group in groups.items():
        print('>>>', key)
        for t in group:
            print(t.url)
        print()


def main():

    print_tabs_by_group()

    # move_domain_to_new_window('www.youtube.com')

    # close_tabs([t for t in tabs if t.url == 'https://www.youtube.com/'])


if __name__ == '__main__':
    main()
