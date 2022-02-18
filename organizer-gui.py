#!/usr/bin/python

"""
Copyright (C) <2022>  <Carlos P Castro>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
from geopy.geocoders import Nominatim
import tkinter as tk
from tkinter import filedialog, Radiobutton, Button, Label, IntVar, StringVar
import os


def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def get_labeled_exif(exif):
    labeled = {}
    for (key, val) in exif.items():
        labeled[TAGS.get(key)] = val

    return labeled


def get_geotagging(exif):
    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                print("No se encontró etiqueta EXIF de geotag")
                return None
            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]

    return geotagging


def convert_to_degrees(value):
    d = value[0]
    m = value[1]
    s = value[2]

    return d + (m / 60.0) + (s / 3600.0)


def organize(value, path):
    if path == "":
        return

    file_path = path

    if file_path != "":
        # Si se organiza por fecha
        if value == 0:
            for photo in os.listdir(file_path):
                if photo.endswith(".jpg") or photo.endswith(".jpeg"):
                    exif = get_exif(os.path.join(file_path, photo))

                    if not exif:
                        print("No se encontró data EXIF")
                        return

                    labeled = get_labeled_exif(exif)
                    date = labeled["DateTime"]
                    date = date.split(" ")
                    print(date[0])
                    dirname = date[0].replace(":", "-")
                    if not os.path.isdir(os.path.join(file_path, dirname)):
                        os.mkdir(os.path.join(file_path, dirname))
                    os.replace(os.path.join(file_path, photo),
                               os.path.join(file_path, dirname) + "/" + photo)
        # Si se organiza por localización
        elif value == 1:
            for photo in os.listdir(file_path):
                if photo.endswith(".jpg") or photo.endswith(".jpeg"):
                    print(photo)
                    exif = get_exif(os.path.join(file_path, photo))

                    if not exif:
                        print("No se encontró data EXIF")
                        return

                    geotags = get_geotagging(exif)

                    if geotags is None:
                        continue

                    lat = geotags["GPSLatitude"]
                    lon = geotags["GPSLongitude"]

                    lat_ref = geotags["GPSLatitudeRef"]
                    lon_ref = geotags["GPSLongitudeRef"]

                    if lat_ref == "S":
                        lat_in_deg = -abs(convert_to_degrees(lat))
                    else:
                        lat_in_deg = convert_to_degrees(lat)

                    if lon_ref == "W":
                        lon_in_deg = -abs(convert_to_degrees(lon))
                    else:
                        lon_in_deg = convert_to_degrees(lon)

                    locator = Nominatim(user_agent="PhotoOrganizer")
                    coordinates = str(lat_in_deg) + ", " + str(lon_in_deg)
                    location = locator.reverse(coordinates)

                    dirname = location.raw["display_name"]
                    if not os.path.isdir(os.path.join(file_path, dirname)):
                        os.mkdir(os.path.join(file_path, dirname))
                    os.replace(os.path.join(file_path, photo),
                               os.path.join(file_path, dirname)
                               + "/" + photo)
    else:
        return


def get_directory():
    global dir_path_string
    global label_text
    dir_path = filedialog.askdirectory()
    dir_path_string.set(dir_path)

    if dir_path_string.get() == "":
        label_text.set("Seleccionar Directorio...")
    else:
        label_text.set(dir_path_string.get())


def main():
    root = tk.Tk()
    root.title("Organizador de fotos")
    root.iconphoto(True, tk.PhotoImage(file="icon.png"))
    root.geometry('640x360')

    global dir_path_string
    dir_path_string = StringVar()

    global label_text
    label_text = StringVar()
    label_text.set("Seleccionar Directorio...")

    dir_label = Label(root, textvariable=label_text, pady=20)
    dir_label.pack()

    dir_button = Button(root, text="Buscar directorio", command=get_directory)
    dir_button.pack()

    var = IntVar()
    radio_date = Radiobutton(root, text="Organizar por fecha.", variable=var,
                             value=0)
    radio_date.pack()

    radio_gps = Radiobutton(root, text="Organizar por localización.",
                            variable=var, value=1)
    radio_gps.pack()

    submit_button = Button(root, text="Organizar", command=lambda:
                           organize(var.get(), dir_path_string.get()))
    submit_button.pack()

    root.mainloop()


if __name__ == "__main__":
    main()
