# MTGP1P1
Creates P1P1 Ratings

Requires python, LGBMRegressor, and pygsheets to run. You need to create a file called secrets.json using [these steps](https://pygsheets.readthedocs.io/en/stable/authorization.html).

Updatesheet is the function you want to call inside the python script.

I regressed 17Lands draft data to the [Google Spreadsheet](https://docs.google.com/spreadsheets/d/1WXUXAMrO33FZMPYJp9hDfMtlGpMyJJcNpcUUp_bZmTQ) provided by u/TheLovelyArcher.

I had to do significant feature engineering. I took Games Played and normalized it by rarity so that the games played value used by the regressor shows how many times the average rarity a card was played.

Games takes the number of games that a card was played and divides it by the mean number of times a card was seen for that rarity.

For example (from THB draft), Wrap in Flames was played in 41 games, the average common was played in about 368 games so far in drafts on 17lands. Therefore, we know that Wrap in Flames is played very rarely, and should be a low pick.
