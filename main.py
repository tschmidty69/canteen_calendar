import wpparser
import argparse
import re
from datetime import datetime
from pprint import pp
from PIL import Image, ImageOps, ImageDraw, ImageFont

parser = argparse.ArgumentParser(
                    prog='export-events',
                    description='Converts wordpress event export '
                                'to a useable calendar'
                    )
parser.add_argument('-d', '--debug', action='store_true', 
                    help='Enable debug output',
                    default=False)
args = parser.parse_args()

def main():
    events = wpparser.parse("./export-events.xml")

    lines = []

    if args.debug > 2: pp(events)

    for event in events["posts"]:
        if "tribe_events" in event.get("post_type"):
            date = event.get("postmeta").get("_EventStartDate")
            if (date and datetime.fromisoformat(date) > datetime.today()):
                day = datetime.fromisoformat(date).strftime('%m%d')
                day_of_week = datetime.fromisoformat(date).strftime('%a')
                time = datetime.fromisoformat(date).strftime('%I:%M %p').replace("0", " ", 1)
                lines.append({day: f"{day_of_week} {time} {event.get('title')}"})
                if args.debug:
                    print(f"Event {event.get('title')} on {date}")
    if args.debug:
        print("=======================")
    month = datetime.today().month
    if args.debug:
        for event in sorted(lines, key=lambda d: list(d.keys())):
            for key, value in event.items():
                if args.debug and month == int(key[0:2]):
                    print(f"\n {datetime(2024, month, 1).strftime('%B')} Events\n")
                    month+=1
                day = f"{key[len(key)-2:]}"
                print(f"{day} {value}")

    calendar = Image.new(mode="RGB", size=(1080,1920), color=(64, 64, 64))
    with Image.open("canteenmonthlyposterheader.jpg") as header:
        calendar.paste(ImageOps.contain(header, (1080, int(1980*.27))), (0,0))
    with Image.open("canteenmonthlyposterfooter.jpg") as footer:
        calendar.paste(ImageOps.contain(footer, (1080, int(1980*.27))), (0,int(1980*.82)))

    font = ImageFont.truetype(r'arialbd.ttf', 24)
    header_font = ImageFont.truetype(r'arialbd.ttf', 40)

    text = ImageDraw.Draw(calendar)

    month = datetime.today().month
    list_start = int(1980*.26)
    list_spacing = int(1980*.016)
    for event in sorted(lines, key=lambda d: list(d.keys())):
        for key, value in event.items():
            list_start += list_spacing
            if list_start+list_spacing > int(1980*.82):
                break
            if args.debug and month == int(key[0:2]):
                text.text((0, list_start), f"{datetime(2024, month, 1).strftime('%B')} Events",
                        font=header_font, fill=(255,255,255))
                month+=1
                list_start += list_spacing*2
            day = f"{key[len(key)-2:]}"

            text.text((0, list_start), f"  {day} {value}", font=font, fill=(255,255,255))


    calendar.show()
    calendar.save("canteenmonthlyposter.jpg")

if __name__=="__main__": 
    main() 