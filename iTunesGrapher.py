__author__ = 'DanielGoldberg'

# !/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3 as lite
import plistlib
import numpy as np
import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import difflib #for use with fuzzywuzzy


def write_database(filename, database):
    con = lite.connect(database)

    print("Reading xml file...")
    pl = plistlib.readPlist(filename)

    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS Tunes")
        cur.execute(
            "CREATE TABLE Tunes(Song TEXT, Artist TEXT, Album_Artist TEXT, Album TEXT, Play_Count INT, Date_Added TEXT, "
            "Y_Added INT, Y_M_Added INT, M_Added INT, Skip_Count INT, Genre TEXT, Kind TEXT, Size INT, Time INT, Year INT, "
            "Bit_Rate INT, Sample_Rate INT, Disabled BOOL)")
        count = 0

        for tracks in pl['Tracks']:

            count = count + 1

            sys.stdout.write('Wrote %d songs to database \r' % (count))

            sys.stdout.flush()

            try:
                name = pl['Tracks'][tracks]['Name']
            except:
                name = ""

            try:
                artist = pl['Tracks'][tracks]['Artist']
            except:
                artist = ""

            try:
                album_artist = pl['Tracks'][tracks]['Album Artist']
            except:
                album_artist = ""

            try:
                album = pl['Tracks'][tracks]['Album']
            except:
                album = ""

            try:
                play_count = pl['Tracks'][tracks]['Play Count']
            except:
                play_count = 0

            try:
                date = pl['Tracks'][tracks]['Date Added']

            # print "year"+str(year)
            # print "year_month"+str(year_month)
            # print "month"+str(month)

            except:
                date = ""

            year = str(date.year)
            month = date.month
            if len(str(month)) == 1:
                year_month = str(year) + "-0" + str(month)
            else:
                year_month = str(year) + "-" + str(month)

            try:
                skip = pl['Tracks'][tracks]['Skip Count']
            except:
                skip = ""

            try:
                genre = pl['Tracks'][tracks]['Genre']
            except:
                genre = ""

            try:
                kind = pl['Tracks'][tracks]['Kind']
            except:
                kind = ""

            try:
                size = pl['Tracks'][tracks]['Size']
            except:
                size = 0

            try:
                time = pl['Tracks'][tracks]['Total Time']
            except:
                time = 0

            try:
                track_year = pl['Tracks'][tracks]['Year']
            except:
                track_year = 0

            try:
                bit = pl['Tracks'][tracks]['Bit Rate']
            except:
                bit = 0

            try:
                sample = pl['Tracks'][tracks]['Sample Rate']
            except:
                sample = 0

            try:
                unchecked = pl['Tracks'][tracks]['Disabled']
            except:
                unchecked = False

            # print name+","+artist+","+album+","+str(play_count)

            cur.execute(
                "INSERT INTO Tunes (Song, Artist, Album_Artist, Album, Year, Time, Play_Count, Date_Added, Y_Added, "
                "Y_M_Added, M_Added, Skip_Count, Genre, Kind, Size, Bit_Rate, Sample_Rate, Disabled) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    name, artist, album_artist, album, track_year, time, play_count, date, year, year_month, month,
                    skip,
                    genre, kind, size, bit, sample, unchecked))

        print('Wrote %d songs to database \r' % count)


def graph_library_summary(database):
    con = lite.connect(database)

    with con:

        cur = con.cursor()

        # -- Top 13 Most Played Artists --
        cur.execute("SELECT Artist, Sum(Play_Count) FROM Tunes GROUP BY Artist ORDER BY Sum(Play_Count) DESC LIMIT 13")

        artists = cur.fetchall()

        # -- Top 13 Most Played Albums --
        cur.execute(
            "SELECT Album, Artist, Sum(Play_Count) FROM Tunes WHERE Album !='' GROUP BY Album ORDER BY Sum(Play_Count) DESC LIMIT 13")

        albums = cur.fetchall()

        cur.execute("SELECT Y_Added, Count(Song) FROM Tunes GROUP BY Y_Added")

        years = cur.fetchall()

        cur.execute("SELECT M_Added, Count(Song) FROM Tunes GROUP BY M_Added")

        months = cur.fetchall()

        # -- Top 20 Genres by Song Count--
        cur.execute(
            "SELECT Genre, Count(Genre) FROM Tunes WHERE Genre !='' GROUP BY Genre ORDER BY Count(Genre) DESC LIMIT 20")

        genres1 = cur.fetchall()

        # -- Top 20 Genres by Play Count --
        cur.execute(
            "SELECT Genre, Sum(Play_Count) FROM Tunes WHERE Genre !='' GROUP BY Genre ORDER BY Sum(Play_Count) DESC LIMIT 20")

        genres2 = cur.fetchall()

        # -- Average Bit Rate --
        cur.execute("SELECT Avg(Bit_Rate) FROM Tunes WHERE Bit_Rate !=0")

        bitrate = cur.fetchall()
        
        # -- Top 20 Most Skipped Songs --
        #cur.execute("SELECT Song, Artist, Album, Sum(Play_Count), Sum(Skip_Count) FROM Tunes ORDER BY Sum(Skip_Count) DESC LIMIT 20")

        #skipped = cur.fetchall()

    print "---- Genres by Song Count ----"
    print genres1

    print "---- Genres by Play Count ----"
    print genres2

    print "---- Average Bit Rate ----"
    print bitrate[0][0]
    
    #print "---- Most Skipped Songs ----"
    #print skipped

    dates = []
    nums = []

    dates_m = []
    nums_m = []

    artist_list = []
    album_counts = []

    album_list = []

    for row in years:
        dates.append(str(row[0]))
        nums.append(row[1])

    for row in months:
        dates_m.append(str(row[0]))
        nums_m.append(row[1])

    count = 1
    for artist in artists:
        artist_list.append(str(count) + ". " + str(artist[0]) + " -- " + str(artist[1]))
        album_counts.append(artist[1])
        count = count + 1

    count2 = 1
    for album in albums:
        album_list.append(str(count2) + ". " + str(album[0]) + " - " + str(album[1]) + " -- " + str(album[2]))
        album_counts.append(album[1])
        count2 = count2 + 1

    fig = plt.figure(figsize=(10, 7))
    plot1 = plt.subplot(2, 2, 1)

    index = np.arange(len(dates))

    plt.bar(index, nums)
    plt.xticks(index, dates, ha="left")
    plot1.set_title('Songs Added by Year', fontweight='bold')

    plot2 = plt.subplot(2, 2, 2)

    index_2 = np.arange(len(dates_m))

    x_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    plt.bar(index_2, nums_m)
    plt.xticks(index_2, x_labels, ha="left")
    plot2.set_title('Songs Added by Month', fontweight='bold')

    plot3 = plt.subplot(2, 2, 3)

    x = .185
    y = .925

    for item in artist_list:
        plot3.text(x, y, item, ha="left", va="center")
        y = y - .07

    plt.xticks(())
    plt.yticks(())
    plot3.set_title('Top Artists by Play Count', fontweight='bold')

    plot4 = plt.subplot(2, 2, 4)

    x = .01
    y = .925

    for item in album_list:
        plot4.text(x, y, item, ha="left", va="center")
        y = y - .07

    plt.xticks(())
    plt.yticks(())
    plot4.set_title('Top Albums by Play Count', fontweight='bold')

    plt.tight_layout()
    plt.show()


def graph_genres(database, printer=False):

    con = lite.connect(database)

    with con:
        cur = con.cursor()

        albums = cur.fetchall()

        # -- Top 20 Genres by Song --
        cur.execute("SELECT Genre, Count(Genre) FROM Tunes WHERE Genre !='' GROUP BY Genre ORDER BY Count(Genre) DESC")

        genres1 = cur.fetchall()

        # -- Top 20 Genres by Play Count --
        cur.execute(
            "SELECT Genre, Sum(Play_Count) FROM Tunes WHERE Genre !='' AND Play_Count!=0 "
            "GROUP BY Genre ORDER BY Sum(Play_Count) DESC")

        genres2 = cur.fetchall()

        cur.execute("SELECT Y_Added, Count(Song) FROM Tunes GROUP BY Y_Added")

        years = cur.fetchall()

        cur.execute("SELECT M_Added, Count(Song) FROM Tunes GROUP BY M_Added")

        months = cur.fetchall()

    genres = []

    genre_names = []
    genre_nums = []

    if printer==True:
        print "---- Genres by Play Count ----"

    for i in range(0, len(genres2)):
        genre_names.append(genres2[i][0])
        genre_nums.append(genres2[i][1])

    smart_genre_names = []
    smart_genre_nums = []

    def fuzzy_combine(genre_names):

        sum = genre_nums[0]
        curr_genre = genre_names[0]

        genre_names.pop(0)
        genre_nums.pop(0)

        choices = process.extract(curr_genre, genre_names, limit=100)

        same = []

        for names in choices:
            if names[1] >= 92:
                same.append(names[0])

        pop_list = []
        if printer==True:
            print "Genre = " + curr_genre

        matches = []
        matches.append(curr_genre)

        for y in same:
            matches.append(y)
            if printer==True:
                print "Matches = " + str(y)

            index = genre_names.index(y)

            pop_list.append((y, index))

        pop_list.sort(key=lambda tup: tup[1], reverse=True)
        #print "pop list sorted = "
        #print pop_list

        pop_list2 = []

        for i in range(0, len(pop_list)):
            pop_list2.append(pop_list[i][1])

        for z in pop_list2:
            #print "z = "+str(z)

            #print genre_names[z]

            sum = sum + genre_nums[z]

            genre_names.pop(z)
            genre_nums.pop(z)

        #print genre_names

        smart_genre_names.append(curr_genre)
        smart_genre_nums.append(sum)

        if len(genre_names) != 0:
            genres.append(matches)

            #print smart_genre_names
            #print smart_genre_nums
            
            if printer==True:
                print "------"

            fuzzy_combine(genre_names)

    fuzzy_combine(genre_names)
    
    if printer==True:
        print smart_genre_names
        print smart_genre_nums

    graphable_names = smart_genre_names[:13]
    graphable_nums = smart_genre_nums[:13]

    sum_others = 0
    for i in range(14, len(smart_genre_names)):
        sum_others = sum_others + smart_genre_nums[i]

    graphable_names.append("Other Genres")
    graphable_nums.append(sum_others)

    fig = plt.figure()
    fig.suptitle('Genres by Play Count', fontsize=14, fontweight='bold')

    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'red', 'green', 'orange', 'pink', 'purple', 'white']

    p = plt.pie(graphable_nums, labels=graphable_names, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')

    w = p[0][0]

    fig.add_subplot(111)


    class PieEventHandler:
        def __init__(self, p):
            self.p = p
            self.fig = p[0].figure
            self.ax = p[0].axes
            self.fig.canvas.mpl_connect('button_press_event', self.onpress)

        def onpress(self, event):
            if event.inaxes != self.ax:
                return

            for w in self.p:
                (hit, _) = w.contains(event)
                if hit:
                    if w.get_label() == "Other Genres":
                        print genres[10:]
                    else:
                        index = smart_genre_names.index(w.get_label())

                        print genres[index]


    handler = PieEventHandler(p[0])

    plt.show()


def main():
    num_arguments = len(sys.argv)

    if num_arguments == 1:
        print("Please provide iTunes xml file")
    elif num_arguments == 2:
        file_input = sys.argv[1]

        if file_input.endswith(".db"):
            database = file_input

            graph_library_summary(database)

        else:

            write_database(file_input, "iTunes.db")

            graph_library_summary("iTunes.db")

    elif num_arguments == 3:
        filename = sys.argv[1]
        database = sys.argv[2]

        write_database(filename, database)

        graph_library_summary(database)
    else:
        print("Too many arguments. Please provide iTunes_xml_file desired_database_name")


if __name__ == '__main__':
    main()