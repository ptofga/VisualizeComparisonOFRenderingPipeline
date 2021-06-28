import os
import mplcursors
import pandas
import matplotlib.pyplot as plt

comparison_df = pandas.DataFrame()
platform_list = []
# number of compared GPU metric data
numberofGPU = 0
symbol_list = []
peak_drawcall_no = []
# read threshold file and get threshold
with open("threshold.txt") as f:
    threshold = float(f.readline())

# read information file
info_df = pandas.read_csv("Information.csv")

# read GPU duration from each metric data exported from GPA and make new DataFrame
for (index, row) in info_df.iterrows():
    numberofGPU += 1
    temp_df = pandas.read_csv(row.FileName)
    if row.Brand == "Intel" or row.Brand == "intel":
        comparison_df[row.Platform] = temp_df["GPU Duration"]
    else:
        comparison_df[row.Platform] = temp_df["GPU Elapsed Time"]
    platform_list.append(row.Platform)
    mean = comparison_df[row.Platform].values.mean()


plt.rcParams['figure.figsize'] = (16.0, 4.0)
comparison_df.plot()

# get all No. of Draw Call which performance is huge different
def get_peaks(dataframe):
    peak_list = []
    for (index, value) in dataframe.iterrows():
        # get max and min of value
        temp_list = []
        for i in range(numberofGPU):
            temp_list.append(float(value[i]))
        if max(temp_list) / max(min(temp_list),1) >= threshold and max(temp_list) >= mean:
            peak_list.append((index, max(temp_list)))
            peak_drawcall_no.append(index)
    return peak_list

# check if symbol file exist
if os.path.exists("symbol.csv"):
    symbol_df = pandas.read_csv("symbol.csv")
    for (no, value) in symbol_df.iterrows():
        str_list = value.Region.split('\\')
        symbol_list.append(str_list[-1])
# write symbol to compare dateframe
    comparison_df['Symbol'] = symbol_list

# save comparison_df to file
    comparison_df.to_csv("comparison.csv")

for l in get_peaks(comparison_df):
    plt.annotate(l[0], l)

# filter peak draw call and save to peak list file.
    peak_df = comparison_df.iloc[peak_drawcall_no]
    peak_df.to_csv("peakdrawcall.csv")


# construct title
title_str = ""
for s in info_df.Platform:
    title_str += s + " "
#:"+str(int(1000*1000/comparison_df[s].values.sum()))+"FPS "
plt.title(title_str)
plt.xlabel("No. of draw call")
plt.ylabel("draw call cost(us)")

# save diagram to png file
plt.savefig("comparison.png", dpi=300)

cursor = mplcursors.cursor(hover=True)


@cursor.connect("add")
def on_add(sel):
    index = int(sel.target.index)
    comment_str = ''
    for (i, v) in comparison_df.iterrows():
        if i == index:
            for j in platform_list:
                comment_str += " " + j + ":" + str(v[j]) + "us"
            break
    if symbol_list.__len__() > 0:
        sel.annotation.set_text(
            'Draw call No.{}\n{}\n{}'.format(int(sel.target.index), symbol_list[int(sel.target.index)], comment_str))
    else:
        sel.annotation.set_text(
            'Draw call No.{}\n{}'.format(int(sel.target.index), comment_str))


plt.show()

