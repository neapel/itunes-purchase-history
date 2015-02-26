# Dump iTunes purchase history to CSV.

As part of a kafkaesque nightmare during which iTunes decided to delete a few year's worth of content I purchased from my account I had to give them a list of order IDs because "you deleted everything, please restore everything" was somehow not enough.

Anyway. Here's how to intercept iTunes' ridiculous communications with its homeworld in order to extract a list that's actually readable (naturally iTunes doesn't let you select or copy the text).

First we need to install [mitmproxy](http://mitmproxy.org/doc):

```
pip install mitmproxy
```

Start it to intercept your system's traffic, keep it running. The inline script doesn't modify the flow, it just extracts the relevant rows and writes them into the given CSV file on exit.

```
mitmproxy -s 'purchases.py out.csv' --socks -b 127.0.0.1 -p 8080
```

Set it as the current proxy in your system (probably a terrible idea)

```
networksetup -listallnetworkservices
networksetup -getsocksfirewallproxy 'Wi-Fi'
networksetup -setsocksfirewallproxy 'Wi-Fi' '127.0.0.1' '8080'
```

Don't forget to unset the proxy after you're done:

```
networksetup -setsocksfirewallproxystate 'Wi-Fi' 'off'
```

Now intercepted connections should begin to appear in the mitmproxy window. Navigate to [mitm.it](http://mitm.it), download the certificate, open it, install it in your keyring (probably a terrible idea, don't forget to uninstall it after you're done)

Now open iTunes, go to **Store → View account**, **Purchase History**, **See all**. Click **Next** until you have viewed all batches of previous orders (iTunes doesn't have an API but instead sends XML descriptions of the complete views. For some reason this includes an entire list of available Podcast genres in every response. The script attempts to find the table used to display the list of purchases and extracts the fields. Even when iTunes shows an ellipsis, the field text include the full purchase ID) 

Mitmproxy should have intercepted iTunes' traffic and handed it to the script for extraction, exit by pressing **q** and answering the prompt with **y**, this will write the CSV file.

Load the generated CSV file into Numbers.app and calculate the sum total of your purchases. My god.


### Offline processing

Use mitmdump to process a captured file:

```
mitmproxy -w out.flows --socks -b 127.0.0.1 -p 8080
mitmdump -n -s "purchases.py out.csv" -r out.flows
```