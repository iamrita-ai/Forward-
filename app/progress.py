import math
from datetime import timedelta

def humanbytes(size):
    """Convert Bytes To Human Readable Format"""
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    """Convert Milliseconds To Human Readable Format"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "") + \
          ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def progress_bar(current, total):
    """Generate Progress Bar String"""
    percentage = current * 100 / total
    progress = "●" * int(percentage // 5) + "○" * (20 - int(percentage // 5))
    return f"[{progress}]"

async def progress_for_pyrogram(current, total, ud_type, message, start):
    """Display Progress Bar For Pyrogram Downloads/Uploads"""
    from time import time
    from config import PROGRESS_DELAY
    
    now = time()
    diff = now - start
    if round(diff % float(PROGRESS_DELAY)) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        progress_str = f"""{ud_type}
{progress_bar(current, total)}
◌Progress😉: 〘 {round(percentage, 2)}% 〙
Done: 〘{humanbytes(current)} of {humanbytes(total)}〙
◌Speed🚀: 〘 {humanbytes(speed)}/s 〙
◌Time Left⏳: 〘 {TimeFormatter(time_to_completion)} 〙"""

        await message.edit_text(progress_str)
