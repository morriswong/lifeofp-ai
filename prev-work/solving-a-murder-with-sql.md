Solving a murder with…SQL?
==========================

Fun way to practise your SQL skills!
------------------------------------

[![Morris Wong](https://miro.medium.com/v2/resize:fill:64:64/1*lAXiT4V5BvkDHh0QnTk9Iw.jpeg)](https://medium.com/?source=post_page---byline--ec6cd7faeb79---------------------------------------)

[Morris Wong](https://medium.com/?source=post_page---byline--ec6cd7faeb79---------------------------------------)

5 min read

·

Jan 30, 2021

[nameless link](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fvote%2Fp%2Fec6cd7faeb79&operation=register&redirect=https%3A%2F%2Ftuewithmorris.medium.com%2Fsolving-a-murder-with-sql-ec6cd7faeb79&user=Morris+Wong&userId=ea11ad1f31be&source=---header_actions--ec6cd7faeb79---------------------clap_footer------------------)

--

1

[nameless link](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2Fec6cd7faeb79&operation=register&redirect=https%3A%2F%2Ftuewithmorris.medium.com%2Fsolving-a-murder-with-sql-ec6cd7faeb79&source=---header_actions--ec6cd7faeb79---------------------bookmark_footer------------------)

Listen

Share

![captionless image](https://miro.medium.com/v2/resize:fit:2000/format:webp/0*dvq2mXe5Jku1S8Af.png)

If you are a newbie trying to sharpen your SQL skills, this SQL game created by the Northwestern University Knight Lab would be one of the interesting place to start.

### SQL Murder Mystery

```
[https://mystery.knightlab.com/](https://mystery.knightlab.com/)
```

Instead of any typical SQL tutorial that asked you to query for the sake of query, this game has also challenged us on one of the most underrated skills on using SQL:

> What is the question that one should ask in the first place?

With that in mind, now all you have is a “case” and some SQL tables, how would you solve it?

### The Case

A crime has taken place and the detective needs your help. The detective gave you the crime scene report, but you somehow lost it. You vaguely remember that the crime was a **​murder​** that occurred sometime on ​**Jan 15, 2018​** and that it took place in ​**SQL City​**. Start by retrieving the corresponding crime scene report from the police department’s database.

### The Tables

*   crime_scene_report
*   drivers_license
*   person
*   facebook_event_checkin
*   interview
*   get_fit_now_member
*   get_fit_now_check_in
*   income
*   solution (okay this doesn’t count)

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*gNLFpwPg9QfZTFqvrhZ2PA.png)

So now detective, who is the murderer?

Finding the murderer
--------------------

> _SPOILERS ALERT: THIS WILL REVEAL WHO IS THE MURDERER!_

The first thing to do? Well, we need to dig out the case first! I did that by finding all the murder cases that happened in SQL city.

> You vaguely remember that the crime was a **​murder​** that occurred sometime on ​**Jan 15, 2018​** and that it took place in ​**SQL City​**.

```
SELECT *
FROM crime_scene_report
WHERE city = 'SQL City' AND type = 'murder'
```![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ZyteLVLxhggxmcwayyqKDQ.png)

Since the case is on Jan 15, it would be the last case in this table. The description also tells us there are two witness. Let's go talk to them!

Talking to the **witnesses**
----------------------------

From what we saw in the case description, there are two witness. Let's find out who they are.

> The first witness lives at the last house on "Northwestern Dr".

```
SELECT *
FROM person
WHERE address_street_name = 'Northwestern Dr'
ORDER BY address_number DESC -- Order the address number from largest to smallest
Limit 1; -- Only pick the first result
```![captionless image](https://miro.medium.com/v2/resize:fit:1188/format:webp/1*sp86mQFd8l-OJSGMyODJcA.png)

> The second witness, named Annabel, lives somewhere on "Franklin Ave".

```
SELECT *
FROM person
WHERE address_street_name = 'Franklin Ave' AND name LIKE '%Annabel%'
```

So the witness are Morty Schapiro and Annabel Miller. Let see what they have to say.

```
SELECT *
FROM interview
WHERE person_id in (14887, 16371)
```![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*tgXtYvAL4A9TLTuJL4r4JA.png)

Looks like there are some new leads! So it happened in a gym, with a car license plate and a membership number on the gym bag. Also one of them recognised the killer about a week ago in the gym. Let’s trace these leads now and see what happened.

The leads
---------

So far from what the witnesses said, there are some leads around the car plates, gym membership number and checkins. Let’s now look at them one by one

> The man got into a car with a plate that included “H42W”.

```
SELECT *
FROM drivers_license
LEFT JOIN person
ON drivers_license.id = person.license_id
WHERE plate_number LIKE '%H42W%'
```![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*P64pfhDAfahoUVk7zxm2Fw.png)

Since one of the witness says the murderer is a male, we got two suspect here now: Jeremy Bowers and Tushar Chandra, which are both male. Let see the other lead about the gym membership.

> The membership number on the bag started with “48Z”, Only gold members have those bags

```
SELECT *
FROM get_fit_now_member
LEFT JOIN get_fit_now_check_in
ON get_fit_now_member.id = get_fit_now_check_in.membership_id
WHERE (get_fit_now_member.id LIKE '48Z%' and membership_status = 'gold') OR name LIKE '%Annabel%'
```![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*QBtqEcgBxbptGYo8JhUJ2w.png)

Bingo! We saw Jeremy Bowers again! And here is the murderer…or is he?

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*srNJrrxz9Xr8e7EH0x_0SA.png)

Well, seems like there is more to it! Let see what Jeremy Bowers have to say

```
SELECT *
FROM interview
WHERE person_id = 67318
```![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*My6tJciLkx18fe2evjA2Kg.png)

So he is actually a hitman! Who is behind all this?

The real murderer?
------------------

Who is the real murderer then? I am going to challege myself here to use only two queries to find out.

Let start by looking at the Model S first.

> I don't know her name but I know she's around 5'5" (65") or 5'7" (67"). She has red hair and she drives a Tesla Model S.

```
SELECT *
FROM drivers_license
LEFT JOIN person
ON drivers_license.id = person.license_id
WHERE car_make = 'Tesla'
AND car_model = 'Model S'
AND hair_color = 'red'
AND gender = 'female'
```![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*yw-h3IUml1LumGH-NNeIYg.png)

And now we have 3 suspects. Next thing to check is if they went to the SQL Symphony Concert 3 times!

> I know that she attended the SQL Symphony Concert 3 times in December 2017.

```
SELECT person_id, name, event_name, count(*) as attended_times
FROM facebook_event_checkin
LEFT JOIN person
ON facebook_event_checkin.person_id = person.id
WHERE date >= 20171201 AND date <= 20171231 and event_name LIKE '%Symphony%' AND person_id in (99716, 90700, 78881)
GROUP BY person_id
ORDER BY attended_times DESC
```![captionless image](https://miro.medium.com/v2/resize:fit:906/format:webp/1*P5kycgUDvLJtZIN31NFKzg.png)

Bingo!

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*NQ0XM0qW7P3UtU-o_5bWVA.png)

Final thoughts
--------------

This is definitely a fun way to practise your SQL skills as it imitates what a real life scenario would be, which is just round and rounds of questions that gets you to the destination.

There are still things like window functions or Common Table Expressions that has yet been covered here and hopefully there would be something coming up from the amazing team that created this!