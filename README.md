# connect-four

This is an implementation of the popular Connect Four game, played over SMS or in an interactive shell.

By default, the code runs as a CGI script on top of Twilio and MySQL. I didn't use Django or Flask because I was running this in a sharing hosting environment and don't have access to those. The code will take the phone number of the sender, look up the current state in a MySQL database, run the user's input move, save the state, and output back in SMS.

After setting this up the webhook, text PLAY to your Twilio number to get started.

The code can also be run in an interactive shell. Comment/uncomment in the main function in connectfour.py to run it locally without Twilio.
