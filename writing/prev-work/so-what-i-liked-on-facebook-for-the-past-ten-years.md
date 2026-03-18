Finding your liked pages on Facebook
====================================

So… what I Liked on Facebook for the past ten years? Retrieving what pages I have liked on Facebook is…not easy
---------------------------------------------------------------------------------------------------------------

[![Morris Wong](https://miro.medium.com/v2/resize:fill:64:64/1*lAXiT4V5BvkDHh0QnTk9Iw.jpeg)](https://medium.com/?source=post_page---byline--8f78486b4758---------------------------------------)

[Morris Wong](https://medium.com/?source=post_page---byline--8f78486b4758---------------------------------------)

4 min read

·

Feb 17, 2019

[nameless link](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fvote%2Fp%2F8f78486b4758&operation=register&redirect=https%3A%2F%2Ftuewithmorris.medium.com%2Fso-what-i-liked-on-facebook-for-the-past-ten-years-8f78486b4758&user=Morris+Wong&userId=ea11ad1f31be&source=---header_actions--8f78486b4758---------------------clap_footer------------------)

--

[nameless link](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F8f78486b4758&operation=register&redirect=https%3A%2F%2Ftuewithmorris.medium.com%2Fso-what-i-liked-on-facebook-for-the-past-ten-years-8f78486b4758&source=---header_actions--8f78486b4758---------------------bookmark_footer------------------)

Listen

Share

![captionless image](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*ljtGgQ0Wb4b37A2nAm6iWA.jpeg)

Despite all the #deletefacebook movement, [Facebook management are still relatively stable](https://www.recode.net/2018/5/22/17340694/facebook-hiring-executive-management-team-mark-zuckerberg) and I am still scrolling through my News Feed every day. For some reason, I just always managed to find interesting content from the all the interesting pages that I have liked over the years.

But there is obviously frustration as well, such as it is not easy to find and browse your own data. For example, how many pages you have liked over the past 10 years and which year you liked the most pages? There is NO WAY to find this out from your Facebook profile. I decided to do something about it.

### Facebook Graph API

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/0*A5mncLlIt8FZQEc_)

Enter [Graph API Explorer](https://developers.facebook.com/docs/graph-api/explorer/) from Facebook. In fact, we can access our own data via this API console. The permission here that we are looking for is [user_likes](https://developers.facebook.com/docs/graph-api/reference/user/likes/), where it returns all the Pages the person (aka you) has liked. That’s exactly what we need!

There are a number of code samples that you can use from once you get what you wanted in the explorer. In my case, I am going to use Python and therefore I am just going to use the Curl snippet and do simple requests.

Now here comes the code. I have wrote a simple Python script so that it can save you from the hassle of writing it again. So after the a few dozen API calls, I managed to get ALL of the pages that I have liked that goes way back to 2009!

Now I can easily see all the pages that I have liked via a csv file…or is there a better way?

### “Explore” the Google Spreadsheet

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/0*CNhGvWYz_l1f3YJh.gif)

While csv is one of the most popular format for data like this. Tools like Google Spreadsheet is in fact already so powerful that it can plot graph for us! Using the [gspread](https://github.com/burnash/gspread) module, you can easily upload the csv onto a specific Google Spreadsheet by the spreadsheet ID.

All you need to do is enable the sheets API and get the credentials for [OAuth,](https://gspread.readthedocs.io/en/latest/) as well as creating a new sheet and share the sheet to the service account of the sheets API in the Google Cloud Console. Find out more from the code below:

And here is what I found with a click of the “Explore” button:

![Seems like I liked most of the pages in 2017](https://miro.medium.com/v2/resize:fit:1200/format:webp/1*2fqO6g7SUExRoijqm6PMVw.png)![And I liked most of the pages at the end and the beginning of the year](https://miro.medium.com/v2/resize:fit:1200/format:webp/1*eJYBi-D695GWL3xTlPxURw.png)![And I liked a lot more pages in the afternoon then other periods](https://miro.medium.com/v2/resize:fit:1200/format:webp/1*V_uiV_Y5aX4V9fv0Z8l-QA.png)

### The not so easy next step

What’s next? Obviously is to let everyone to be able to use this without all the hassle above…which turns out to be not so easy.

Since the [Cambridge Analytica Scandal](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&cd=1&cad=rja&uact=8&ved=2ahUKEwipmqes-cLgAhWKP3AKHQpWArkQFjAAegQIBxAB&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FFacebook%25E2%2580%2593Cambridge_Analytica_data_scandal&usg=AOvVaw07KmvD0rJgDLqSRfDGzb-m), Facebook has a more strict policy on allow developers to create app out of Facebook data. In fact, I have tried multiple time on applying for an App Review, but got rejected multiple times. I hope that one day, all the people can just see what they have liked with a click of a button. [Let me know](mailto:morris.chw@outlook.com) if you have any idea on that! (I have heard that it takes months to get the approval…)

Hope this post is helpful in helping you to find out more about the Facebook pages you ever liked. Now let me get back to scrolling my News Feed and find more pages to like.