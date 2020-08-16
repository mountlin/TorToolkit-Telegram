
import logging
import math
import os
import time
from .Human_Format import human_readable_bytes,human_readable_timedelta
from ..core.getVars import get_val
from ..core.database_handle import TtkUpload
#logging.basicConfig(level=logging.DEBUG)

async def progress(current,total,message,file_name,start,cancel_msg=None):

    if cancel_msg is not None:
        # dirty alt. was not able to find something to stop upload
        # todo inspect with "StopAsyncIteration"
        db = TtkUpload()
        if db.get_cancel_status(cancel_msg.chat_id,cancel_msg.id):
            del db
            raise Exception("cancel the upload")
        del db

    now = time.time()
    diff = now - start
    time_out = get_val("EDIT_SLEEP_SECS")

    if round(diff % time_out) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = human_readable_timedelta(seconds=elapsed_time/1000)

        estimated_total_time = human_readable_timedelta(seconds=estimated_total_time/1000)


        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join([get_val("COMPLETED_STR") for i in range(math.floor(percentage / 5))]),
            ''.join([get_val("REMAINING_STR") for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))
        
        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            human_readable_bytes(current),
            human_readable_bytes(total),
            human_readable_bytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            if not message.photo:
                await message.edit(
                    text="{}\n {}".format(
                        file_name,
                        tmp
                    )
                )
            else:
                await message.edit(
                    caption="{}\n {}".format(
                        file_name,
                        tmp
                    )
                )
        except Exception as e:
            logging.error(e)
            pass
