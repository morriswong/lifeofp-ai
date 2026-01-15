Visualising the World Press Freedom Index 2020 with Tableau
===========================================================

Same data, different dimensions
-------------------------------

[![Morris Wong](https://miro.medium.com/v2/resize:fill:64:64/1*lAXiT4V5BvkDHh0QnTk9Iw.jpeg)](https://medium.com/?source=post_page---byline--a10790cd90ae---------------------------------------)

[Morris Wong](https://medium.com/?source=post_page---byline--a10790cd90ae---------------------------------------)

4 min read

·

Aug 10, 2020

[nameless link](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fvote%2Fp%2Fa10790cd90ae&operation=register&redirect=https%3A%2F%2Ftuewithmorris.medium.com%2Fvisualising-the-world-press-freedom-index-2020-with-tableau-a10790cd90ae&user=Morris+Wong&userId=ea11ad1f31be&source=---header_actions--a10790cd90ae---------------------clap_footer------------------)

--

[nameless link](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2Fa10790cd90ae&operation=register&redirect=https%3A%2F%2Ftuewithmorris.medium.com%2Fvisualising-the-world-press-freedom-index-2020-with-tableau-a10790cd90ae&source=---header_actions--a10790cd90ae---------------------bookmark_footer------------------)

Listen

Share

As a regular Tableau user by day, every time you see a visualisation out there, you would start to wonder how we can drill down into the data a bit better? And then one day I came across the latest world press freedom index visualisation from the Reporters Without Borders which looks like this:

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*QjIjSGSRMl09HBtHzZPGzA.png)

Well…not bad. And then I clicked through the the tabs and find out there is an “Index details” page where you can actually download the data in csv.

> Sounds like we have a visualisation coming in!

> TL;DR: My visualisation for the data is at [this link](https://public.tableau.com/views/WorldPressFreedonIndex/TheWorldPressFreedomIndexDashboard?%3Alanguage=en&%3Adisplay_count=y&publish=yes&%3Aorigin=viz_share_link), feel free to check it out!

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*X3BK-5rGYErIbZcpqJIuGQ.png)

### Preparing the data

While in the real world, 95% of the data is usually messy and needs some preparation, this time around the data is relatively simple can clean. All we have is list of countries, their scores and their ranking. There is only one small problem in this dataset, that is it only shows the country name but not the respective continents. I have found [this region code](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv) on Github that can be further linked to the world press freedom ranking dataset.

Visualising the data
--------------------

While there is a lot to talk about, I would like to this visualisation into three parts:

*   Maps,
*   Stats table and
*   Top and bottom tables

### Maps

One of the big feature on Tableau is the ability to show maps graphs relatively easily. The data table already have the names of the country, and that would automatically be recognised with the right longitude and latitude. I added the rank progression as the text overlay as well as color coded rise and fall in ranking as green and red respectively.

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*cTLRioOX_GoPPCeWccNGwA.png)

### Stats table

Another cool feature using Tableau is the ability to quickly calculate some stats to help one to have a basic understanding of what a datasets looks like. I have separated these stats data into different continents so that the ranking can be compared across them. Things like highest/lowest ranking, progression as well as the average and median rank and score that builds the ranking is included as well.

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*PSuFnGZGELL7qZ1131ZJag.png)

We can start to see some interesting things here now:

*   The average and median ranking is more or less close to each other except for Europe, where there is a 13.07 rank difference
*   The Net Progression Rank, which is the sum of the both positive and negative rank progression is dropping for Americas and Oceania, as much as -24 and -19 respectively
*   While Africa and Asia lags behind, Africa actually has a better average (37 vs 44.52) and median (33 vs 42) score

And there is always more to find out, this is just a sneak peak!

### Top and bottom tables

I am not sure if this is the right name, but this is another cool things in Tableau that allows you to use calculated field and parameters to customise what you wanted to see on the dashboard.

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*23yoc826hZ1uE8Tkh_wNlw.png)

With the help from the two filtering fields, customising the table to see would be much easier without having to see the whole table of data, for example, below is the top/bottom 2 of progression and rank of all Asian countries.

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*3nCDJBzOwjWberp5Vli_DA.png)

Tip of the iceberg?
-------------------

I am sure up till now, you may noticed that seems my interpretation is a bit off and that could might just be true. Visualising the data is only one of the many steps in data. I can think of things top of my mind like:

*   How does the data is complied in the first place? (What is the source?)
*   Is there another other hidden trends in the data? (Can look at the individual scores as well apart from just the ranking)
*   Grouping the data in another fashion? (Such as trade partnerships instead of continents)

The list goes on! And that is why drilling into data is such an interesting thing to do.

Thanks for reading!
-------------------

What else can you spot in the data? Or have you come up with something more amazing? Feel free to share this around and hope this helps you to understand more about using Tableau as a data visualisation tool.