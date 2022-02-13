import hypixel_api, imtui, curses, time

def ViewItemStats(stdscr, hypixel:hypixel_api.SkyblockApi, last_item_json):
    while True:
        stdscr.clear()
        stdscr.refresh()
        item_name = last_item_json.get('product_id', 'API_ERROR!')

        frame = imtui.Frame(title=item_name, width=stdscr.getmaxyx()[1] - 4, height=stdscr.getmaxyx()[0] - 4, voffset=2, hoffset=2, hallign=imtui.Location.Left, vallign=imtui.Location.Top)
        imtui.RenderTitle(stdscr, frame, params=curses.A_BOLD | curses.A_STANDOUT, full_width=True)

        curses_window = frame.CreateCursesWindow(stdscr)

        sell_summary = last_item_json.get('sell_summary', {})
        buy_summary =last_item_json.get('buy_summary', {})
        table_data = {
            'buy orders': [i + 1 for i in range(30)],
            'amount     ': [row.get('amount', None) for row in sell_summary],
            'price      ': [row.get('pricePerUnit', None) for row in sell_summary],
            'orders ': [row.get('orders', None) for row in sell_summary],

            'sell offers': [i + 1 for i in range(30)],
            'amount      ': [row.get('amount', None) for row in buy_summary],
            'price       ': [row.get('pricePerUnit', None) for row in buy_summary],
            'orders': [row.get('orders', None) for row in buy_summary],
        }

        table = imtui.Table(data=table_data, height=frame.height, width=frame.width)
        imtui.RenderTable(curses_window, table)

        time.sleep(10)
        del curses_window
        last_item_json = hypixel.Bazaar().get('products', {}).get(item_name, {})

def StartApiInterface(stdscr, hypixel:hypixel_api.SkyblockApi):
    item = 'ENCHANTED_CAKE'

    item_json = hypixel.Bazaar().get('products', {}).get(item)
    ViewItemStats(stdscr, hypixel, item_json)
