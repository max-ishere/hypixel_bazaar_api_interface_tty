import curses
import time
from curses.textpad import rectangle, Textbox
import pathlib
import httpx
import gnupg
import imtui

def SavePlainKey(apikey:str) -> str:
    config_path = pathlib.Path('~/.config/hypixel_api').expanduser()
    config_path.mkdir(parents=True, exist_ok=True)
    keyfile = config_path / 'key.txt'
    with keyfile.open('w') as f:
        f.write(apikey)
    keyfile.chmod(0o600)

    return str(keyfile)

def SaveEncryptedKey(apikey:str, passwd:str):
    encrypted = str(gnupg.GPG().encrypt(apikey, symmetric=True, passphrase=passwd, armor=True, encrypt=False))

    config_path = pathlib.Path('~/.config/hypixel_api').expanduser()
    config_path.mkdir(parents=True, exist_ok=True)
    keyfile = config_path / 'key.gpg'

    with keyfile.open('w') as f:
        f.write(encrypted)

    keyfile.chmod(0o600)

    return str(keyfile)

def StoreApiKey(stdscr) -> str:
    stdscr.clear()
    termh, termw = stdscr.getmaxyx()

    KEY_LENGTH = 37
    V_BOX_MARGIN = 3
    BOX_WIDTH = KEY_LENGTH + V_BOX_MARGIN * 2
    BOX_HEIGHT = 10

    H_BEGIN_BOX = max(0, int(termh / 2 - BOX_HEIGHT / 2))
    V_BEGIN_CONTENT = max(1, int(termw / 2 - BOX_WIDTH / 2) + V_BOX_MARGIN)

    frame = imtui.Frame(title='Setup - API Key Validation', height= BOX_HEIGHT, width= KEY_LENGTH + 4 + V_BOX_MARGIN * 2)

    imtui.RenderBorder(stdscr, frame)
    imtui.RenderTitle(stdscr, frame, params=curses.A_STANDOUT | curses.A_DIM | curses.A_BOLD, full_width=True)

    renderable_frame = imtui.Frame(height=BOX_HEIGHT, width=KEY_LENGTH+4)
    curses_window = renderable_frame.CreateCursesWindow(stdscr)

    imtui.RenderLabel(curses_window, imtui.Label(text='Hypixel API Key', style=curses.A_BOLD, height=1, width=renderable_frame.width, voffset=1))
    apikey_field = imtui.InputField(password=True, max_lenght=KEY_LENGTH, voffset=2)
    imtui.RenderInputField(curses_window, apikey_field)

    imtui.RenderLabel(curses_window, imtui.Label(text='Use `/api new` on the Hypixel server to obtain your api key or paste in an existing one.', height=3, width=renderable_frame.width, voffset=4))

    progress = imtui.ProgressBar(status='Waiting for API key', progress_total = 3, voffset = -1, vallign=imtui.Location.Bottom, width=renderable_frame.width, progress=0)
    imtui.RenderProgressBar(curses_window, progress)
    apikey = apikey_field.GetInput(curses_window)

    progress.IncrementStatus('Contacting api.hypixel.net')
    imtui.RenderProgressBar(curses_window, progress)
    responce = httpx.get('https://api.hypixel.net/key', params={'key':apikey}).json()

    if responce.get('success', False):
        progress.IncrementStatus('Contacting api.mojang.com')
        imtui.RenderProgressBar(curses_window, progress)
        minecraft_name =httpx.get(f'''https://api.mojang.com/user/profile/{responce.get('record',{}).get('owner','')}''').json().get('name','API_ERROR')
    else:
        progress.progress += 1

    progress.IncrementStatus('Key info gathered')
    imtui.RenderProgressBar(curses_window, progress)

    curses_window.clear()
    curses_window.refresh()

    if responce.get('success') == True:
        frame.title = 'Setup - Key data confirmation'
        imtui.RenderTitle(stdscr, frame, params=curses.A_BOLD | curses.A_STANDOUT | curses.A_DIM, full_width=True)

        imtui.RenderLabel(curses_window, imtui.Label(text=f'Owner: {minecraft_name}', height=1, width=renderable_frame.width, voffset=1))
        imtui.RenderLabel(curses_window, imtui.Label(text=f'''Query limit per minute: {responce.get('record',{}).get('queriesInPastMin','API_ERROR!')} / {responce.get('record',{}).get('limit','API_ERROR!')}''', height=1, width=renderable_frame.width, voffset=2))
        imtui.RenderLabel(curses_window, imtui.Label(text=f'''Total queries: {responce.get('record',{}).get('totalQueries','API_ERROR!')}''', height=1, width=renderable_frame.width, voffset=3))

        imtui.RenderLabel(curses_window, imtui.Label(text='Save this key? [y/n]', height=1, width=renderable_frame.width, vallign=imtui.Location.Bottom, voffset=-1))


        option = imtui.AskOptions(stdscr, 'yn', 'y')

        assert option in 'yn'
        if option == 'n':
            return None

    else:
        frame.title = 'Setup - Invalid API key'
        imtui.RenderTitle(stdscr, frame, params=curses.A_BOLD | curses.A_STANDOUT | curses.A_DIM, full_width=True)
        imtui.RenderLabel(curses_window, imtui.Label(text=f'''Key rejected: {responce.get('cause', 'API_ERROR!')}''', height=3, width=renderable_frame.width, voffset=1))

        imtui.RenderLabel(curses_window, imtui.Label(text='Press any key to quit API key setup', height=1, width=renderable_frame.width, vallign=imtui.Location.Bottom, voffset=-1))

        stdscr.getch()

        return None

    curses_window.clear()
    curses_window.refresh()

    frame.title = 'Setup - Saving key localy'
    imtui.RenderTitle(stdscr, frame, params=curses.A_BOLD | curses.A_STANDOUT | curses.A_DIM, full_width=True)

    imtui.RenderLabel(curses_window, imtui.Label(text='Create passphrase for your key', style=curses.A_BOLD, height=3, width=renderable_frame.width, voffset=1))
    imtui.RenderLabel(curses_window, imtui.Label(text='Empty for no password', style=curses.A_DIM, height=3, width=renderable_frame.width, voffset=3))

    passwd_field = imtui.InputField(password=True, max_lenght=KEY_LENGTH, voffset=2)
    imtui.RenderInputField(curses_window, passwd_field)

    passwd = passwd_field.GetInput(curses_window)

    if passwd == '':
        keypath = SavePlainKey(apikey)
    else:
        keypath = SaveEncryptedKey(apikey, passwd)

    imtui.RenderLabel(curses_window, imtui.Label(text=f'Saved keyfile to\n{keypath}', height=2, width=renderable_frame.width, vallign=imtui.Location.Bottom, voffset=-1))
    time.sleep(3)
    return apikey

def RetrieveKey(stdscr) -> str:
    termh, termw = stdscr.getmaxyx()

    PASSWORD_LENGTH = 37
    V_BOX_MARGIN = 3
    BOX_WIDTH = PASSWORD_LENGTH + 4 + V_BOX_MARGIN * 2
    BOX_HEIGHT = 9

    H_BEGIN_BOX = max(0, int(termh / 2 - BOX_HEIGHT / 2))
    V_BEGIN_CONTENT = max(1, int(termw / 2 - BOX_WIDTH / 2) + V_BOX_MARGIN)

    stdscr.clear()
    frame = imtui.Frame(title='Retrieving API Key', height=BOX_HEIGHT, width=BOX_WIDTH)
    renderable_frame = imtui.Frame(height=BOX_HEIGHT, width=PASSWORD_LENGTH+4)
    curses_window = renderable_frame.CreateCursesWindow(stdscr)

    imtui.RenderBorder(stdscr, frame)
    imtui.RenderTitle(stdscr, frame, curses.A_BOLD | curses.A_REVERSE | curses.A_DIM, full_width=True)
    stdscr.refresh()

    config_path = pathlib.Path('~/.config/hypixel_api').expanduser()
    config_path = config_path.expanduser()

    plain_keyfile = config_path / 'key.txt'
    encrypted_keyfile = config_path / 'key.gpg'

    if plain_keyfile.exists():
        with plain_keyfile.open('r') as f:
            imtui.RenderLabel(curses_window, imtui.Label(text='Plaintext API key found at', width=renderable_frame.width, voffset=1, height=1,))
            imtui.RenderLabel(curses_window, imtui.Label(text=str(plain_keyfile), width=renderable_frame.width, voffset=2, height=3,))
            apikey = f.readline()

    elif encrypted_keyfile.exists():
        with encrypted_keyfile.open('r') as f:
            attempts = 0
            encrypted_key = str('\n'.join(f.readlines()))

            while True:
                curses_window.clear()
                curses_window.refresh()

                imtui.RenderLabel(curses_window, imtui.Label(text='API key password', style=curses.A_BOLD, width=renderable_frame.width, voffset=1, height=1,))

                passwd_field = imtui.InputField(max_lenght=PASSWORD_LENGTH, voffset=2, password=True)
                imtui.RenderInputField(curses_window, passwd_field)

                if attempts >= 2:
                    imtui.RenderLabel(curses_window, imtui.Label(text=f'If you forgot your password then delete\n{str(encrypted_keyfile)}', style=curses.A_DIM, width=renderable_frame.width, voffset=6, height=3,))


                while True:
                    passwd = passwd_field.GetInput(curses_window)
                    if passwd != '':
                        break

                decrypted = gnupg.GPG().decrypt(encrypted_key, passphrase=passwd)

                if decrypted.ok:
                    apikey = str(decrypted)
                    break
                else:
                    imtui.RenderLabel(curses_window, imtui.Label(text=f'Key Decryption failed.\nGNUPG error: {decrypted.status}', style=curses.A_DIM, width=renderable_frame.width, voffset=3, height=3,))
                    attempts += 1

                    time.sleep(3)
                    continue

    else:
        imtui.RenderLabel(curses_window, imtui.Label(text=f'No key found, exiting.', width=renderable_frame.width, height=1))
        time.sleep(3)
        return None

    return apikey

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()

    config_path = pathlib.Path('~/.config/hypixel_api').expanduser()

    apikey = None
    while apikey == None:
        if config_path.joinpath('key.txt').exists() or config_path.joinpath('key.gpg').exists():
            apikey = RetrieveKey(stdscr)

        else:
            apikey = StoreApiKey(stdscr)



    stdscr.clear()
    stdscr.refresh()

    time.sleep(3)
    curses.curs_set(1)


if __name__ == '__main__':
    curses.wrapper(main)
